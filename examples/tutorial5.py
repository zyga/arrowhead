#!/usr/bin/env python3
"""
Tutorial Lesson 5
=================

This is the fith tutorial arrowhead program.

This is a dummy program building on the previous lesson. It introduces one more
element but is really just more complex than previous examples so that you can
play around with the graph viewer.

So the new thing. Previously we got the name of the step object. This is good
for some queer encapsulation. Typically you will want to store attributes on
the flow object itself. This is exactly what we're doing here.

As you will see if you run this program with -t console, you will see the state
of the flow now contains the name attribute. The flow can store anything as
long as it doesn't clash with any step of names. There's no protection for that
yet so be careful.

So with that out of the way, play with the '-t x11' mode if you also add
'--delay=1'. This is a simple trick to see as the flow progresses from place to
place. The current step is highlighted with blue. There's nothing special about
it but it can be useful to look at when debugging complex flows that misbehave.

You can also add the --pdb option to jump into pdb before running each step
method. The execution environment there is specific to the runner that
arrowhead comes with (so you need to look at what the variables are to use it
properly) but the idea is very powerful. You could do other stuff (other than
running pdb) instead. You could even store the state of the flow and resume it
later. Anything is possible.

That's the end of the tutorial for the current release. Enyjoy, open issues,
get in touch with me (@zygoon on twitter). Thanks for reading this.
"""
from arrowhead import Flow, step, arrow, main


class Greeting(Flow):
    """
    A hello-world flow
    """

    @step(initial=True)
    @arrow('ask_for_name')
    def hi(step):
        print("Hi!")

    @step
    @arrow('special_greet', value='zyga')
    @arrow('do_nothing', value='')
    @arrow('clean_console', error=KeyboardInterrupt)
    @arrow('greet')
    def ask_for_name(step, flow):
        flow.name = input("What is your name? ")
        return flow.name

    @step(accepting=True)
    def do_nothing(step):
        pass

    @step(level=1)
    @arrow('ask_for_name')
    def clean_console(step):
        print()

    @step
    @arrow('bye')
    def special_greet(step):
        print("Hey boss!")

    @step
    @arrow('bye')
    def greet(step, flow):
        print("Hey, welcome {}!".format(flow.name))

    @step(accepting=True)
    def bye(step):
        print("Bye!")


if __name__ == '__main__':
    main(Greeting)
