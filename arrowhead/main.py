import argparse
import errno
import pdb
import subprocess
import tempfile
import time

from arrowhead.core import Arrow, Step
from arrowhead.errors import ProgrammingError
from arrowhead.errors import GraphvizNotInstalled
from arrowhead.inspector import print_dot_graph
from arrowhead.inspector import print_flow_state


def main(flow_cls, argv=None):
    """
    Command line wrapper for any flow.

    This wrapper allows to execute any flow directly from command line. Several
    command line options are exposed for debugging and analysis.
    """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.set_defaults(action='run')
    group.add_argument(
        '--run', action='store_const', const='run', dest='action',
        help="Run the flow (default)")
    group.add_argument(
        '--dot', action='store_const', const='dot', dest='action',
        help="Export the flow in dot format")
    group.add_argument(
        '--preview', action='store_const', const='preview', dest='action',
        help="Show the flow diagram in a X11 window")
    parser.add_argument(
        '-t', '--trace', choices=['console', 'x11'],
        help="Display visual trace of flow execution")
    parser.add_argument(
        '--pdb', default=False, action='store_true',
        help="Jump into the pdb between steps (for --run)")
    parser.add_argument(
        '--delay', default=0, action='store', type=int,
        help="Insert artificial delays between steps")
    ns = parser.parse_args(argv)
    if ns.action == 'dot':
        print_dot_graph(flow_cls)
        return
    # Create a viewer
    if ns.trace == 'console':
        viewer = ConsoleFlowViewer()
    elif ns.trace == 'x11':
        viewer = X11FlowViewer()
    else:
        viewer = DummyViewer()
    # Preview the flow
    if ns.action == 'preview':
        if isinstance(viewer, DummyViewer):
            viewer = ConsoleFlowViewer()
        try:
            viewer.update(flow_cls)
            viewer.wait_for_exit()
        finally:
            viewer.close()
    elif ns.action == 'run':
        try:
            retval = _run_flow(flow_cls, viewer, ns.pdb, ns.delay)
            if retval is not None:
                print("arrowhead> flow returned: {!r}".format(retval))
        except ProgrammingError as exc:
            raise SystemExit(exc)
        else:
            viewer.wait_for_exit()
        finally:
            viewer.close()


def _run_flow(flow_cls, viewer, use_pdb, delay):
    flow = flow_cls(autostart=False)
    viewer.update(flow, '_start')
    if use_pdb:
        print("arrowhead> about to start flow execution (pdb)")
        pdb.set_trace()
    for obj in flow._run():
        if isinstance(obj, Step):
            step = obj
            viewer.update(flow, step.Meta.name)
            if delay:
                print("arrowhead> waiting for {}s".format(delay))
                time.sleep(delay)
            if use_pdb:
                print("arrowhead> current step: {} (pdb)".format(step))
                pdb.set_trace()
        elif isinstance(obj, Arrow):
            # TODO: make the viewer capable of showing the active arrow
            # arrow = obj
            # print("Following", arrow)
            pass
    viewer.update(flow, '_end')
    if use_pdb:
        print("arrowhead> finished flow (pdb)")
        pdb.set_trace()
    return getattr(flow, 'return')


class DummyViewer:

    def update(self, flow, active_step_name=None):
        pass

    def close(self):
        pass

    def wait_for_exit(self):
        pass


class ConsoleFlowViewer:

    def update(self, flow, active_step_name=None):
        print_flow_state(flow, active_step_name)

    def close(self):
        pass

    def wait_for_exit(self):
        while True:
            try:
                input("(control+C to close)")
            except KeyboardInterrupt:
                print()
                break


class X11FlowViewer:

    def __init__(self):
        self.dot_file = tempfile.NamedTemporaryFile(
            mode='w+t', suffix='.dot', encoding='UTF-8')
        self.proc = None

    def update(self, flow, active_step_name=None):
        self.dot_file.seek(0)
        self.dot_file.truncate()
        print_dot_graph(flow, active_step_name, file=self.dot_file)
        self.dot_file.flush()
        if self.proc is None:
            try:
                self.proc = subprocess.Popen(['dot', '-Txlib', self.dot_file.name])
            except OSError as exc:
                if exc.errno == errno.ENOENT:
                    raise GraphvizNotInstalled


    def close(self):
        if self.proc is not None:
            try:
                self.proc.terminate()
            except OSError:
                pass
            self.proc.wait()
        self.dot_file.close()

    def wait_for_exit(self):
        if self.proc:
            print("(close the graphviz window or control+C to close)")
        while True:
            try:
                if self.proc is not None:
                    self.proc.wait()
                break
            except KeyboardInterrupt:
                print()
                try:
                    if self.proc is not None:
                        self.proc.terminate()
                except OSError:
                    pass
