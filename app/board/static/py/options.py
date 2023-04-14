import random
import os


def check_length(value):
    if len(value) > 16:
        return True
    return False


def change_random_pieces_to_queen(value):
    return


class OptionsCommon:
    '''
      pieces = [Q,R,B,N,P,(K white only)]
    '''

    def __init__(self):
        pass

    def b_N1_b1__w_b2_p1(wP, bP):
        bP[3] += 1
        bP[2] += 1
        wP[2] += 1
        wP[3] += 1
        wP[4] += 1

        return bP, wP

    def b_B2__w_b2_p1(wP, bP):
        bP[2] += 2
        wP[2] += 2
        wP[4] += 1

        return bP, wP

    def b_P4__w_b2(wP, bP):
        bP[4] += 5
        wP[2] += 2

        return bP, wP

    def b_P3__w_b1(wP, bP):
        bP[4] += 3
        wP[2] += 1

        return bP, wP

    def b_P3__w_n1(wP, bP):
        bP[4] += 3
        wP[3] += 1

        return bP, wP

    def b_P5__w_p6(wP, bP):
        bP[4] += 5
        wP[4] += 6

        return bP, wP

    def b_P4__w_r1_p1(wP, bP):
        bP[4] += 5
        wP[1] += 1
        wP[4] += 1

        return bP, wP

    def b_N1_P3__w_r1_p1(wP, bP):
        bP[3] += 1
        bP[4] += 3
        wP[1] += 1
        wP[4] += 1

        return bP, wP

    def b_B1_P3__w_r1_p1(wP, bP):
        bP[2] += 1
        bP[4] += 3
        wP[1] += 1
        wP[4] += 1

        return bP, wP

    def b_r1__w_r1_p1(wP, bP):
        bP[1] += 1
        wP[1] += 1
        wP[4] += 1

        return bP, wP

    def b_r1__w_n1_b1_p1(wP, bP):
        bP[1] += 1
        wP[2] += 1
        wP[3] += 1
        wP[4] += 1

        return bP, wP

    def b_r1__w_n2_p2(wP, bP):
        bP[1] += 1
        wP[3] += 2
        wP[4] += 1

        return bP, wP

    def b_r1__w_b2_p2(wP, bP):
        bP[1] += 1
        wP[2] += 2
        wP[4] += 1

        return bP, wP


class OptionsRare:
    def b_r2__w_q1_p2(wP, bP):
        bP[1] += 2
        wP[0] += 1
        wP[4] += 2

        return bP, wP

    def b_q1__w_r1_n1_p2(wP, bP):
        bP[1] += 1
        wP[1] += 1
        wP[3] += 1
        wP[4] += 2

        return bP, wP

    def b_q1__w_r2(wP, bP):
        bP[1] += 1
        wP[1] += 1
        wP[3] += 1
        wP[4] += 2

        return bP, wP

    def b_q1__w_n2_b1_p2(wP, bP):
        bP[0] += 1
        wP[2] += 1
        wP[3] += 2
        wP[4] += 2

        return bP, wP

    def b_r2__w_n2_b2_p2(wP, bP):
        bP[1] += 2
        wP[2] += 2
        wP[3] += 2
        wP[4] += 2

        return bP, wP


def get_common_options():
    return random.sample([m for m in dir(OptionsCommon) if not m.startswith('__')], 3)
