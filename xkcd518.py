#!/usr/bin/env python3
from arrowhead import Flow, step, arrow, main


def ask(prompt):
    answer = None
    while answer not in ('yes', 'no'):
        answer = input(prompt + ' ')
    return answer


class XKCD518(Flow):
    """
    https://xkcd.com/518/
    """

    @step(initial=True, level=1)
    @arrow('do_you_understand_flowcharts')
    def start(step):
        """
        START
        """
        print(step.Meta.label)

    # ---------------

    @step(level=2)
    @arrow(to='good', value='yes')
    @arrow(to='okay_you_see_the_line_labeled_yes', value='no')
    def do_you_understand_flowcharts(step):
        """
        Do you understand flowcharts?
        """
        return ask(step.Meta.label)

    @step(level=2)
    @arrow(to='lets_go_drink')
    def good(step):
        print(step.Meta.label)

    # ---------------

    @step(level=3)
    @arrow(to='hey_I_should_try_installing_freebsd')
    def lets_go_drink(step):
        """
        Let's go drink.
        """
        print(step.Meta.label)

    @step(accepting=True, level=3)
    def hey_I_should_try_installing_freebsd(step):
        """
        Hey, I should try installing freeBSD!
        """
        print(step.Meta.label)

    # ---------------

    @step(level=4)
    @arrow(to='and_you_can_see_ones_labeled_no', value='yes')
    @arrow(to='but_you_see_the_ones_labeled_no', value='no')
    def okay_you_see_the_line_labeled_yes(step):
        """
        Okay. You see the line labeled 'yes'?
        """
        return ask(step.Meta.label)

    @step(level=4)
    @arrow(to='good', value='yes')
    @arrow(to='but_you_just_followed_them_twice', value='no')
    def and_you_can_see_ones_labeled_no(step):
        """
        ...and you can see the ones labeled 'no'?
        """
        return ask(step.Meta.label)

    # ---------------

    @step(level=5)
    @arrow(to='wait_what', value='yes')
    @arrow(to='listen', value='no')
    def but_you_see_the_ones_labeled_no(step):
        """
        But you see the ones labeled "no"?
        """
        return ask(step.Meta.label)

    # ---------------

    @step(accepting=True, level=5)
    def wait_what(step):
        """
        Wait, what!
        """
        print(step.Meta.label)

    # ---------------

    @step(level=6)
    @arrow(to='I_hate_you')
    def listen(step):
        """
        Listen
        """
        print(step.Meta.label)

    @step(accepting=True, level=6)
    def I_hate_you(step):
        """
        I hate you
        """
        print(step.Meta.label)

    # ---------------

    @step(level=5)
    @arrow(to='that_wasnt_a_question', value='yes')
    @arrow(to='that_wasnt_a_question', value='no')
    def but_you_just_followed_them_twice(step):
        """
        But you just followed them twice!
        """
        return ask(step.Meta.label)

    @step(level=5)
    @arrow(to='screw_it')
    def that_wasnt_a_question(step):
        """
        (That wasn't a question)
        """
        print(step.Meta.label)

    @step(level=4)
    @arrow(to='lets_go_drink')
    def screw_it(step):
        """
        Screw it.
        """
        print(step.Meta.label)


if __name__ == '__main__':
    main(XKCD518)
