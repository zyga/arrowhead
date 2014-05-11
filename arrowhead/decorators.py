import functools
import inspect
import types

from arrowhead.core import ErrorArrow
from arrowhead.core import NormalArrow
from arrowhead.core import Step
from arrowhead.core import ValueArrow


def step(func_or_label=None, **kwargs):
    """
    Decorator for converting functions to steps.

    This decorator can be applied in a number of ways::

        @step
        def do_stuff(self):
            pass

        @step
        def do_other_stuff(self):
            pass

    Without any arguments it just creates a step that when executed, will call
    the decorated function. Typically steps will also need to be decorated with
    the @arrow decorator to form a sensible graph but in very simple cases one
    can rely on the top-to-bottom implicit arrows.

    With arguments, one can specify several additional details. The most
    important are the initial and accepting flags::

        @step(initial=True)
        def start(self):
            pass

        @step(accepting=True)
        def stop(self):
            pass

    Within one flow exactly one step must be initial. A ProgrammingError
    exception is raised if that is not the case. All exceptions of this type
    carry additional information to help diagnose the problem.

    All steps have a label. By default, if you don't provide one and the
    decorated function doesn't have a docstring then function name is used as a
    label. Labels are very important as they can be used to 'address' steps
    throughout the graph. Labels can obviously be specified explicitly::

        @step(label="Start your engines!")
        def start_engines(self):
            pass

    As a convention, the first line of the docstring becomes the implicit label
    of any step, unless overridden with an explicit label. This encourages
    documentation and improves the readability of the built-in flow debugger.

        @step
        def load_all_data(self):
            '''
            load all data from the disk

            This long description is not a part of the label. Luckily!
            '''

    .. note::
        The order of @step and @arrow calls is irrelevant.
    """
    if func_or_label is None or isinstance(func_or_label, str):
        if func_or_label is not None:
            kwargs['label'] = func_or_label

        @functools.wraps(func_or_label)
        def step(func):
            return _convert_to_step(func, **kwargs)
        return step
    else:
        return _convert_to_step(func_or_label)


def arrow(to, **kwargs):
    """
    Decorator for attaching arrows between steps.

    :param to:
        step to go to
    :param value:
        (optional) value to associate the arrow with
    :param value:
        (optional) error to associate the arrow with

    In the most basic mode the arrow connects two steps together.  In the
    example below the two steps would create an infinite loop going from the
    first step to the second step and back::

        @arrow('second')
        @step
        def first(self):
            print("First")

        @arrow(to='first')
        @step
        def second(self):
            print("Second")

    Arrows can carry a value condition, such arrows are only followed if the
    ``value`` argument is equal to ``step.value``. This can be used to create
    typical flow control structures. In the example below the step will
    either go left or right, depending on the outcome of a coin toss::

        @arrow('go_left', value='heads')
        @arrow('go_right', value='tails')
        @step
        def fork_in_the_road(self):
            self.value = toss_a_coin()

    Lastly arrows can carry an error condition. This is useful to structure
    abnormal exits so that the program won't crash but instead do something
    sensible for the user. Such arrows are followed if the runtime error
    instance is a subclass of the ``error`` argument. For a contrived example
    let's pretend that the coin can someties land on the side and in that
    case we want to just try again::

        @arrow('go_left', value='heads')
        @arrow('go_right', value='tails')
        @arrow('fork_in_the_road', error=CoinLandedOnTheSide)
        @step
        def fork_in_the_road(self):
            self.value = toss_a_coin()
    """
    target = _resolve_arrow_target(to)
    if 'value' in kwargs:
        value = kwargs.pop('value')
        arrow = ValueArrow(target, value)
    elif 'error' in kwargs:
        error = kwargs.pop('error')
        arrow = ErrorArrow(target, error)
    else:
        arrow = NormalArrow(target)
    if kwargs:
        raise TypeError("stray arguments: {!r}".format(kwargs))

    def decorator(decoratee):
        if isinstance(decoratee, Step):
            step = decoratee
            step.Meta.arrows.append(arrow)
        elif isinstance(decoratee, types.FunctionType):
            func = decoratee
            if not hasattr(func, 'arrows'):
                func.arrows = []
            func.arrows.append(arrow)
        else:
            raise TypeError(
                "unsupported decorated type {}".format(type(decoratee)))
        return decoratee
    return decorator


def _resolve_arrow_target(target):
    """
    Convert arrow target specification to a step name

    :param target:
        arrow target specification
    :returns:
        name of the target step
    :raises TypeError:
        if the target specification is incorrect

    The target specification can be one of three things: a Step class, a
    string or a function. Step classes use cls.Meta.label, functions use
    func.__name__ and strings are used as-is.
    """
    if isinstance(target, type) and issubclass(target, Step):
        return target.Meta.label
    elif isinstance(target, types.FunctionType):
        return target.__name__
    elif isinstance(target, str):
        return target
    else:
        raise TypeError("unsupported target type: {0}".format(type(target)))


def _convert_to_step(func, label=None, initial=None, accepting=False,
                     level=None):
    """
    Convert a step function to a subclass of :class:`Step`

    :param func:
        Function to work with
    :param goto:
        The default step to take next
    :param initial:
        if True, this step will be the initial step of the flow
    :param accepting:
        if True, this step will be an accepting step
    :param level:
        explicit level number for graph layout
    """
    if label is None:
        if func.__doc__:
            label = func.__doc__.lstrip().splitlines()[0]
        else:
            label = func.__name__
    ns = {
        'name': func.__name__,
        'label': label,
        'initial': initial,
        'accepting': accepting,
        'arrows': func.arrows if hasattr(func, 'arrows') else [],
        'needs_flow': 'flow' in inspect.getargspec(func)[0],
        'level': level,
        '__call__': func,
    }
    return type(func.__name__, (Step,), ns)
