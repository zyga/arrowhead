#!/usr/bin/env python3

from arrowhead import Flow, step, arrow, main


class InfiniteLoop(Flow):

    @step(initial=True)
    @arrow('b')
    def a(step):
        print("a")

    @step
    @arrow('a')
    def b(step):
        print("b")


if __name__ == '__main__':
    main(InfiniteLoop)
