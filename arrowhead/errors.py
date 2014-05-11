from arrowhead import BUG_URL
from arrowhead import __version__ as VERSION


class Bug(BaseException):
    """
    Exception for things that indicate arrowhead error
    """
    def __str__(self):
        return '\n'.join([
            "It seems you have found a bug in arrowhead",
            "Please open a ticket on {}".format(BUG_URL),
            "Please attach the text printed below to the bug report",
            "ArrowHead version: {}".format(VERSION),
            super().__str__(),
        ])


class ProgrammingError(Exception):
    """
    Exception raised when flow is constructed incorrectly
    """


class NoInitialStep(ProgrammingError):
    """
    Exception raised when a non-empty flow has no initial steps.

    Any flow graph must have exactly one initial step. Just decide where you
    want to start computing.
    """

    def __str__(self):
        return "No initial step selected"


class DuplicateInitialStep(ProgrammingError):
    """
    Exception raised when there is more than one initial step within one flow

    :ivar old_initial:
        The name of the old (existing) initial step
    :ivar new_initial:
        The name of the new (colliding) initial step

    Any flow graph must have exactly one initial step. To solve this problem
    just figure out which one you want to really be initial.
    """

    def __init__(self, old_initial, new_initial):
        self.old_initial = old_initial
        self.new_initial = new_initial

    def __str__(self):
        return '\n'.join([
            "Duplicate initial step detected.",
            "The step {} was marked as initial".format(self.new_initial),
            "But step {} is already inititial".format(self.old_initial)])

    def __repr__(self):
        return "{}({!r}, {!r})".format(
            self.__class__.__name__, self.old_initial, self.new_initial)


class NoArrowCouldHaveBeenFollowed(ProgrammingError):
    """
    Exception raised when flow cannot continue

    :ivar step:
        The problematic step
    """

    def __init__(self, step):
        self.step = step

    def __str__(self):
        return '\n'.join([
            "No arrow could have been followed from the step {!a}".format(
                self.step.Meta.label),
            "The following arrows were defined:",
        ] + ([
            "    {}".format(arrow) for arrow in self.step.Meta.arrows
        ] or [" (there are no arrows)"]) + [
            "This is the state of this step right now:"
        ] + ([
            "    {k}: {v!r}".format(k=k, v=v)
            for k, v in self.step.__dict__.items()
            if not k.startswith("_")
        ] or [" (there is no state yet)"]))


class NoSuchStep(ProgrammingError):
    """
    Exception raised when a missing step is referenced

    :ivar step_name:
        The problematic step_name
    """

    def __init__(self, step_name):
        self.step_name = step_name

    def __str__(self):
        return "Reference to unknown step {!r}".format(
            self.step_name)


class ConflictingArrow(ProgrammingError):
    """
    Exception raised when arrows are conflicting

    :ivar arrow:
        Arrow that is definitely wrong
    """

    def __init__(self, arrow):
        self.arrow

    def __str__(self):
        return "Conflicting arrow detected: {}".format(self.arrow)
