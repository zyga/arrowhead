#!/usr/bin/env python3
"""
Tutorial Lesson 2
=================

This is the second tutorial arrowhead program.

This program prints either 'heads' or 'tails', depending on a virtual coin
toss. This will require us to move from one of two possible destinations (from
the initial node). We will also learn about basic state handling.

So the flow is composed of three steps. The toss_a_coin step simply returns one
of two strings at random ('heads' or 'tails'). The actual values are identical
to step names but this is just an accident, they have no special meaning.

You will note that the @arrow decorators are now a little different. We now
pass a keyword argument 'value' (it has to be a keyword argument). The return
value of the decorated function is compared against each of the arrows (using
equality operator). The one that matches picks the next destination.

Make sure to run the program and to look at the graphical diagram. You will
note that unlike in the previous graph the arrows are green. The colors are
arbitrary but black arrows are unconditional while green arrows depend on a
particular value.

If you use the console state viewer (./tutorial2.py -t console) you will see
that each step gains a 'return' attribute. The attribute is actually called
return to ensure it doesn't (cannot) clash with anything assigned by any
particular step (since return is a keyword). This will be expanded upon later
but each step object can hold any attribute that can be assigned from within
the step function. This state is available to (potentially) every other step,
as we will see later.
"""

import random

from arrowhead import Flow, step, arrow, main


class CoinToss(Flow):

    @step(initial=True)
    @arrow(to='heads', value='heads')
    @arrow(to='tails', value='tails')
    def toss_a_coin(step):
        print("Tossing a coin...")
        return random.choice(['heads', 'tails'])

    @step(accepting=True)
    def heads(step):
        print("Heads!")

    @step(accepting=True)
    def tails(step):
        print("Tails!")


if __name__ == '__main__':
    main(CoinToss)
