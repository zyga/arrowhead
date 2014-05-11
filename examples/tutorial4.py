#!/usr/bin/env python3
"""
Tutorial Lesson 4
=================

This is the fourth tutorial arrowhead program.

The previous lessons introduced all of the baisc concepts of arrowhead. Now
we'll look at how one can work with flow state.

As established previously, the first argument of each step function refers to a
step object (an instance of a unque Step subclass that is named after the
decorated method name). State objects are instantiated early in flow instance
intialization. You cannot share state between invocations of the same Flow
class as you will be instantiating unique flow objects. That's just for
reference, let's see what we can do instead.

You can assign any attribute of the step object. Typically you will do that so
that other steps can refer to it later. We'll do just that with this greeter
program. The what_is_your_name step assigns the 'name' attribute on the step
object. That attribute is accessed from the greet step, through the flow
argument. The flow argument is a new thing that we haven't seen before, it's
actually the 'self' you would typically expect as it refers to the instance of
the flow itself. Each step becomes a step object that is assigned to the name
of the method. So we can just reach out to each step and see (or alter yaiks!)
anything inside.

There is no error handling in this program but you get the idea. It's very
simple and powerful, when you know which step is responsible for setting the
state you care about. As we'll see later you can also abstract that away.

So there you have it, each step can store any state attribute (except Meta,
that's reserved), then you can each out to any other step by accepting the flow
argument. Through that argument you get the instance of the flow class you are
executing in and you can access each step as it were an attribute.
"""

from arrowhead import Flow, step, arrow, main


class Greeting(Flow):

    @step(initial=True)
    @arrow(to='what_is_your_name')
    def hi(step):
        print("Hi")

    @step
    @arrow(to='greet')
    def what_is_your_name(step):
        step.name = input("what is your name? ")

    @step(accepting=True)
    def greet(step, flow):
        print("Hey {name}".format(name=flow.what_is_your_name.name))


if __name__ == '__main__':
    main(Greeting)
