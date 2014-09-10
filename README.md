ArrowHead
=========


        Micro-framework for flowchart computing
         _   _   _   _               _  _   _
    ____|_|_|_|_|_|_| |_| | |___|_|_|__|_|_| \____________\
        | | | \ | \ |_| |_|_|   | | |_ | | |_/            /


Arrowhead is a framework for constructing flow charts composed of steps
connected by (possibly) conditional branches. Such flows can be executed,
inspected (at runtime) and visualized (for documentation and verification)

The idea of flowchart computing is designed in a way that mimics a hand-made
drawing, typically on a white-board or a piece of paper, that describes some
process as a graph of interconnected steps.

Traditionally, once designed, the process is implemented as a collection of
functions and classes. Very often the original idea of how the process was supposed
to work lost, especially after making changes over time. Usually it is
impossible to easily reconstruct the initial idea from a complex implementation
of that idea.

As an added issue, it is non-trivial to create derivative processes that
somehow override, change, replace or remove parts of the process. This can
affect one step or a particular group of steps.

The arrowhead framework aims to address both problems.

The process (or flow, as some communities like to call it) is encoded as a
class derived from the :class:`Flow` class. Inside each method decorated with
the ``@step`` decorator becomes a distinct step.

Each step may connect to other steps with arrows. This can be done with the
@arrow decorator. Arrows may be constrained by passing ``value=`` keyword
argument. Such arrows are followed only when ``step.value`` is equal to
``arrow.value``. Arrows may also be constrained by passing ``error=`` keyword
argument. Such arrows are followed only when an exception of that (or
derivative) type is raised by the step function. Arrows without either
constraint are always followed.

Each flow needs to have one initial and at least one accepting step. Flow
execution always starts with the initial step. The initial step can be changed
in derivative classes, in that case the base initial step is no longer
considered initial.
