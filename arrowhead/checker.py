class FlowVisitor:

    def visit_Flow(self, flow):
        pass

    def visit_Step(self, step):
        pass

    def visit_Arrow(self, arrow):
        pass


def explore_flow(flow, visitor):
    visitor.visit_Flow(flow)
    for step in flow.Meta.steps.values():
        visitor.visit_Step(step)
        for arrow in step.Meta.arrows:
            visitor.visit_Arrow(arrow)
