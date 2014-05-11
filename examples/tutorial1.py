#!/usr/bin/env python3
"""
Tutorial Lesson 1
=================

This is the first tutorial arrowhead program.

This program simply prints 'hello world' they way you would expect it to.  In
doing so it introduces three core features of arrowhead: flow, step and arrow.

Flow - the flow class is where flow programs are defined.  While they look like
normal classes they behave a little bit like magic so keep that in mind.

@step - the step decorator can convert regular methods into special step
classes. Each step class wraps the method that was decorated and adds local
state and meta-data. Local state like just like local variables that you would
assign in regular programs but they live beyond the lifetime of the call to the
wrapped method.

It may be easy to miss but the first argument of each step method is not self
(implying that it would be related to the flow) but actually 'step'. It does in
fact refer to a step object. Step objects (and classes) are entirely empty
except for the ``Meta`` attribute and the __call__ method that is the decorated
function itself. Step management is explained further in the tutorial.

If you don't understand any of that then just keep in mind that @step does
quite a bit of magic and you should not treat anything decorated as such as a
normal method anymore. Oh, and each flow needs at least one accepting state or
it will never stop.

@arrow - the arrow decorator is how you navigate between steps.  Instead of
performing direct calls to other methods you let arrowhead do that for you.
All you have to do is to statically declare where you want to go (and as you
will later see, how to decide which arrow to follow if more than arrow is
used). Arrows are less drastic than '@step' as they simply add some meta-data
that the engine later uses.

That's it for this lesson. Make sure to run this program with '--help' to see
additional options. You can experiment with them all you like. I would
especially recommend '--trace x11' (in this case perhaps with '--delay 5'). For
more hardcore users you will want to see '--dot'.

Read on to tutorial lesson 2 to see subsequent features being introduced.
"""
from arrowhead import Flow, step, arrow, main


class HelloWorld(Flow):

    @step(initial=True)
    @arrow(to='world')
    def hello(step):
        print("Hello...")

    @step(accepting=True)
    def world(step):
        print("... world!")


if __name__ == '__main__':
    main(HelloWorld)
