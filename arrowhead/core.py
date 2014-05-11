import abc
import collections
import sys

from arrowhead.errors import Bug
from arrowhead.errors import ConflictingArrow
from arrowhead.errors import DuplicateInitialStep
from arrowhead.errors import NoArrowCouldHaveBeenFollowed
from arrowhead.errors import NoInitialStep
from arrowhead.errors import NoSuchStep


class StopFlow(Exception):
    """
    Exception that indicates that flow should stop

    This exception is raised internally by :class:`Flow` to stop the flow
    loop.
    """


class Arrow(metaclass=abc.ABCMeta):
    """
    Base class for other arrows
    """

    def __init__(self, target):
        self.target = target

    def __str__(self):
        return "@arrow({!a})".format(self.target)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.target)

    @abc.abstractmethod
    def should_follow(self, step):
        pass


class NormalArrow(Arrow):
    """
    Arrow that is followed if step.raise doesn't exist

    This arrow should be constructed with ``@arrow('target')``.
    """

    # Lowest priority
    priority = 2

    def should_follow(self, step):
        if hasattr(step, 'raise'):
            return False
        return True


class ValueArrow(Arrow):
    """
    Arrow that is followed if step.raise doesn't exist and step.return is equal
    to arrow.value.

    This arrow should be constructed with ``@arrow('target', value=...)``
    """

    # Normal priority
    priority = 1

    def __init__(self, target, value):
        super().__init__(target)
        self.value = value

    def __str__(self):
        return '@arrow({!a}, value={!r})'.format(self.target, self.value)

    def __repr__(self):
        return "{}({!r}, value={!r})".format(
            self.__class__.__name__, self.target, self.value)

    def should_follow(self, step):
        if hasattr(step, 'raise'):
            return False
        if not hasattr(step, 'return'):
            return False
        return getattr(step, 'return') == self.value


class ErrorArrow(Arrow):
    """
    Arrow that is followed if step.raise is is an instance of arrow.error.

    This arrow should be constructed with ``@arrow('target', error=...)``
    """

    # High priority
    priority = 0

    def __init__(self, target, error=None):
        super().__init__(target)
        self.error = error

    def __str__(self):
        return '@arrow({!a}, error={})'.format(
            self.target, self.error.__name__)

    def __repr__(self):
        return "{}({!r}, error={})".format(
            self.__class__.__name__, self.target, self.error.__name__)

    def should_follow(self, step):
        if not hasattr(step, 'raise'):
            return False
        return isinstance(getattr(step, 'raise'), self.error)


class _StepMeta(type):
    """
    Metaclass for all step classes.

    This metaclass is responsible for storing all the step meta-data inside the
    new Meta class. This includes step name (name), label (label), a list of
    arrows (arrows), three flags (initial, accepting, needs_flow) and a
    numerical value used for displaying graphs (level)

    The namespace of the newly created step class is actually empty apart
    from the Meta class and the __call__ method which is copied directly
    from the __call__ method of the original namespace.
    """

    def __new__(mcls, name, bases, namespace, **kwargs):
        metadata = ('name', 'label', 'arrows', 'initial', 'accepting',
                    'needs_flow', 'level')
        for attr in metadata:
            if attr not in namespace:
                # This is an internal error, unless someone really
                # inherits from Step directly
                raise Bug("Step {!a} doesn't have {!a}".format(
                    name, attr))
        new_ns = {
            'Meta': type('StepMeta', (object,), {
                attr: namespace[attr] for attr in metadata
            }),
        }
        new_ns.update({
            key: value
            for key, value in namespace.items()
            if key not in metadata
        })
        return super().__new__(mcls, name, bases, new_ns, **kwargs)


class Step(metaclass=_StepMeta):
    """
    Smallest distinct part of a flow.

    Step classes are typically automatically constructed from functions using
    the :func:`step()` decorator. It is important to note that the argument
    'self' on such functions is *not* the flow class they are defined in but
    the instance of a unique subclass of the Step class.

    As such, methods decorated with '@step' have access to Step APIs, including
    :meth:`goto()` and the :meth:`accepting` property.
    """
    name = "step"
    label = "Step"
    arrows = []
    initial = False
    accepting = False
    needs_flow = False
    level = None

    def __call__(self):
        pass

    def __getattr__(self, attr):
        raise AttributeError(
            "the step {!a} doesn't have state item {!a}".format(
                self.Meta.label, attr))


class _FlowMeta(type):
    """
    Metaclass for all flow classes.

    This metaclass is responsible for collecting steps and determining the
    initial step of a flow. It sets the 'steps' and 'initial' class
    attributes on newly created classes. It also uses an ordered dictionary for
    class namespace to retain step ordering.
    """

    def __new__(mcls, name, bases, namespace, **kwargs):
        initial = mcls._find_initial_step(bases, namespace)
        steps = mcls._find_steps(bases, namespace)
        mcls._sort_arrows(steps)
        mcls._check_arrows(steps)
        if initial is not None:
            mcls._assign_levels(steps, initial)
        namespace['Meta'] = type('FlowMeta', (object,), {
            'steps': steps,
            'initial': initial,
            'levels': max(
                step.Meta.level for step in steps.values()
            ) if steps else 0,
            'name': name,
        })
        return super().__new__(mcls, name, bases, namespace, **kwargs)

    def _check_arrows(steps):
        """
        Check if all arrows are okay
        """
        for step in steps.values():
            # check if targets exist
            for arrow in step.Meta.arrows:
                if arrow.target not in steps:
                    raise NoSuchStep(arrow.target)
            # check if values are unique
            values = set()
            errors = set()
            normal = False
            for arrow in step.Meta.arrows:
                if isinstance(arrow, NormalArrow):
                    if normal:
                        raise ConflictingArrow(arrow)
                    normal = True
                elif isinstance(arrow, ErrorArrow):
                    if arrow.error in errors:
                        raise ConflictingArrow(arrow)
                elif isinstance(arrow, ValueArrow):
                    if arrow.value in values:
                        raise ConflictingArrow(arrow)

    def _find_steps(bases, namespace):
        """
        Build an OrderedDict of all steps
        """
        steps = collections.OrderedDict()
        for base in bases:
            if issubclass(base, Flow):
                steps.update(base.Meta.steps)
        for k, v in namespace.items():
            if isinstance(v, type) and issubclass(v, Step):
                steps[k] = v
        return steps

    def _sort_arrows(steps):
        """
        Sort arrows in order of priority
        """
        for step in steps.values():
            step.Meta.arrows.sort(key=lambda arrow: arrow.priority)

    def _assign_levels(steps, initial):
        branch = collections.namedtuple('branch', 'target level')
        todo = []
        todo.append(branch(steps[initial], 1))
        while todo:
            step, level = todo.pop()
            if step.Meta.level is None:
                step.Meta.level = level
            for arrow in step.Meta.arrows:
                next_step = steps[arrow.target]
                if next_step.Meta.level is None:
                    todo.append(branch(next_step, level + 1))

    def _find_initial_step(bases, namespace):
        base_initial = None
        this_initial = None
        seen_steps = False
        for base in bases:
            if issubclass(base, Flow):
                base_initial = base.Meta.initial
        for k, v in namespace.items():
            if isinstance(v, type) and issubclass(v, Step):
                seen_steps = True
                if v.Meta.initial:
                    if this_initial is None:
                        this_initial = k
                    else:
                        raise DuplicateInitialStep(k, this_initial)
        if this_initial is None:
            this_initial = base_initial
        if this_initial is None and seen_steps:
            raise NoInitialStep()
        return this_initial

    def __prepare__(name, bases, **kwargs):
        return collections.OrderedDict()


class Flow(metaclass=_FlowMeta):
    """
    A set of connected steps.
    """

    def __init__(self, autostart=True):
        # Instantiate all the steps
        for name, step_cls in self.Meta.steps.items():
            setattr(self, name, step_cls())
        if autostart:
            for step in self._run():
                pass

    def _run(self):
        active_step_name = self.Meta.initial
        try:
            while True:
                step = getattr(self, active_step_name)
                yield step
                arrow = self._run_one_step(step)
                yield arrow
                active_step_name = arrow.target
        except StopFlow:
            setattr(self, 'return', getattr(step, 'return'))

    def _run_one_step(self, step):
        # Reset special internal state
        if hasattr(step, 'return'):
            delattr(step, 'return')
        if hasattr(step, 'raise'):
            delattr(step, 'raise')
        # Run the step function
        try:
            if step.Meta.needs_flow:
                setattr(step, 'return', step(self))
            else:
                setattr(step, 'return', step())
        except (KeyboardInterrupt, Exception):
            setattr(step, 'raise', sys.exc_info()[1])
        else:
            # stop the flow if an accepting step succeeds
            if step.Meta.accepting:
                raise StopFlow
        # Find the arrow to follow
        for arrow in step.Meta.arrows:
            if arrow.should_follow(step):
                return arrow
        raise NoArrowCouldHaveBeenFollowed(step)
