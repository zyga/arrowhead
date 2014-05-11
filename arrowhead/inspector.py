import sys

from arrowhead.core import Step
from arrowhead.core import ErrorArrow
from arrowhead.core import NormalArrow
from arrowhead.core import ValueArrow


def print_flow_state(flow, active_step_name=None, file=sys.stdout):
    """
    Display the state of a given flow.

    :param flow:
        A Flow, instance or class
    :param active_step_name:
        (optional) name of the active step
    :param file:
        (optional) file to print to (defaults to sys.stdout)

    This function actually prints() a developer-friendly version of the state
    of the entire flow. The output is composed of many lines. The output will
    contain all of the internal state of the flow (may print stuff like
    passwords if you stored any).
    """
    # show flow name
    print("[{}]".format(flow.Meta.name).center(40, "~"), file=file)
    # show flow global state
    needs_header = True
    for f_k, f_v in flow.__dict__.items():
        # private stuff is private
        if f_k.startswith("_"):
            continue
        # steps are handled later
        if (isinstance(f_v, Step) or
                (isinstance(f_v, type) and issubclass(f_v, Step))):
            continue
        # skip Meta
        if f_k == 'Meta':
            continue
        if needs_header:
            print("STATE:", file=file)
            needs_header = False
        print("{indent}{key}: {value!r}".format(
            indent=" " * 4, key=f_k, value=f_v
        ), file=file)
    # show a list of all the steps, their state as well as a marker that
    # shows where we actively are
    print("STEPS:", file=file)
    for name in flow.Meta.steps.keys():
        step = getattr(flow, name)
        flags = []
        if step.Meta.accepting:
            flags.append('A')
        if step.Meta.initial == name:
            flags.append('I')
        if flags:
            rendered_flags = " ({})".format(''.join(flags))
        else:
            rendered_flags = ""
        if step.Meta.name == active_step_name:
            indent = " => "
        else:
            indent = "    "
        print("{indent}{step}{flags:4}".format(
            indent=indent, flags=rendered_flags, step=step.Meta.label
        ), file=file)
        needs_header = False
        for s_k, s_v in step.__dict__.items():
            if s_k.startswith("_"):
                continue
            # skip Meta
            if s_k == 'Meta':
                continue
            if needs_header:
                print("STATE:", file=file)
                needs_header = False
            print("{indent}{key}: {value!r}".format(
                indent=" " * 8, key=s_k, value=s_v
            ), file=file)
    print("." * 40, file=file)


def print_dot_graph(flow, active_step_name=None, file=sys.stdout):
    """
    Print the dot(1) description of a given flow.

    :param flow:
        A Flow, instance or class
    :param active_step_name:
        (optional) name of the active step
    :param file:
        (optional) file to print to (defaults to sys.stdout)
    """
    print('digraph {', file=file)
    print('\tnode [shape=box, color=black];', file=file)
    print('\tedge [arrowsize=0.5];', file=file)
    print(file=file)
    print('\tsubgraph {', file=file)
    print('\t\tnode [shape=plaintext];', file=file)
    # NOTE: levels + 2 because 0 and max are
    # for _start and _end that are not
    # represented anywhere in the flow. We
    # just add them for graphviz
    print('\t\t{};'.format(
        ' -> '.join(str(i) for i in range(flow.Meta.levels + 2))
    ), file=file)
    print('\t}', file=file)
    print(file=file)
    # NOTE: levels + 2 as above
    levels = {i: [] for i in range(flow.Meta.levels + 2)}
    levels[0].append('_start')
    # NOTE: levels + 1 is the last element
    levels[flow.Meta.levels + 1].append('_end')
    for step in flow.Meta.steps.values():
        levels[step.Meta.level].append(step.Meta.name)
    for level, steps in sorted(levels.items()):
        print('\t{{ rank=same; {}; {}; }}'.format(
            level, '; '.join(steps)
        ), file=file)
    print(file=file)
    if active_step_name == '_start':
        print('\t_start [shape=circle, style=filled,'
              ' fillcolor=blue, label=""];', file=file)
    else:
        print('\t_start [shape=circle, style=filled,'
              ' fillcolor=black, label=""];', file=file)
    for step in flow.Meta.steps.values():
        if step.Meta.initial:
            print('\t_start -> {};'.format(step.Meta.name), file=file)
    print(file=file)
    for step in flow.Meta.steps.values():
        if active_step_name == step.Meta.name:
            print('\t{} [shape={}, label="{}", style=filled, fillcolor=blue, fontcolor=white];'.format(
                step.Meta.name, "box",
                step.Meta.label.replace('"', '\\"')
            ), file=file)
        else:
            print('\t{} [shape={}, label="{}"];'.format(
                step.Meta.name, "box",
                step.Meta.label.replace('"', '\\"')
            ), file=file)
        for arrow in step.Meta.arrows:
            if isinstance(arrow, NormalArrow):
                print('\t{} -> {};'.format(
                    step.Meta.name, arrow.target
                ), file=file)
            elif isinstance(arrow, ValueArrow):
                print('\t{} -> {} [label="{}", color=green];'.format(
                    step.Meta.name, arrow.target, arrow.value
                ), file=file)
            elif isinstance(arrow, ErrorArrow):
                print('\t{} -> {} [label="{}", color=red];'.format(
                    step.Meta.name, arrow.target, arrow.error.__name__
                ), file=file)
        print(file=file)
    if active_step_name == '_end':
        print('\t_end [shape=doublecircle, style=filled, '
              'fillcolor=blue, label=""];', file=file)
    else:
        print('\t_end [shape=doublecircle, style=filled, '
              'fillcolor=black, label=""];', file=file)
    for step in flow.Meta.steps.values():
        if step.Meta.accepting:
            print('\t{} -> _end;'.format(step.Meta.name), file=file)
    print("}", file=file)
