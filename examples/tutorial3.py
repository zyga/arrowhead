#!/usr/bin/env python3
"""
Tutorial Lesson 3
=================

This is the third tutorial arrowhead program.

If you read tutorial 2 you probably know that it was a simple coin-tossing
program. In real applications error handling is the bulk of the boilerplate
boring code that needs to be carefully managed. This is why arrowhead has
explicit support for abnormal exits (exceptions) and this is exactly what we
will learn in this lesson.

So first the program is changed a little. There is a CoinFellOnTheEdge
exception. The initial toss_a_coin step is changed to have 1 in 11 chance of
landing on the edge. If that happens we raise the new exception. There is also
a new type of arrow that is designed to react to exceptions. It is defined with
the error keyword (it has to be a keyword, just like with value). That new
arrow leads to a new step (edge) that leads back to toss_a_coin.

All in all this is pretty simple. In a very very unlucky case the program will
actually never terminate but let's not worry about that now. Run it a few times
(feel free to change the code to make the exception happen more frequently) to
make sure it works as expected.

Have a look at the graph. It will have the new error arrow painted with the red
color. If you use the console tracer (./tutorial3 -t console) you will see that
when the exception is raised the state of the node gains a 'raise' attribute
(not 'return' as it usually does). Again this is so that we never collide with
anything the flow code may normally assign to.

One thing that is not obvious is that unlike value= arrows, error= arrows use
isinstance(). This may make ordering of @arrow decorators significant. Make
sure to match the more specific exceptions before the more generic ones.

As a side note: arrows are actually sorted internally by arrowhead, erorr
arrows take priority (their order is unchanged) followed by value arrows
finally to the plain unconditional arrow. You can use python3 -m pydoc
tutorial3.CoinToss.toss_a_coin.Meta to see the order of arrows in this case.
If you haven't looked at pydoc of flow classes doing so now may be interesting.
Don't worry if you don't understand evetything that is inside flow.Meta and
step.Meta objects.

So there you have it, you can have basic error management now.
"""

import random

from arrowhead import Flow, step, arrow, main


class CoinFellOnTheEdge(ValueError):
    """
    Exception raised when a coin lands on the edge.

    Is that even possible?
    """


class CoinToss(Flow):

    @step(initial=True)
    @arrow(to='heads', value='heads')
    @arrow(to='tails', value='tails')
    @arrow(to='edge', error=CoinFellOnTheEdge)
    def toss_a_coin(step):
        print("Tossing a coin...")
        result = random.choice(['heads'] * 5 + ['tails'] * 5 + ['edge'])
        if result == 'edge':
            raise CoinFellOnTheEdge
        return result

    @step(accepting=True)
    def heads(step):
        print("Heads!")

    @step(accepting=True)
    def tails(step):
        print("Tails!")

    @step
    @arrow(to='toss_a_coin')
    def edge(step):
        print("Woah, it landed on the edge, let me try again")


if __name__ == '__main__':
    main(CoinToss)
