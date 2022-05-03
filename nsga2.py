#!/usr/bin/env python3

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.factory import get_termination
from pymoo.optimize import minimize

from haskell_adaptor import ArrayDecoder, get_coverage

MAX_PRICE = 10
MAX_QTY = 10
MAX_MODAL_QTY = 3
ORD_ENCODED_SIZE = 9
MAX_TC_SIZE = 10
MAX_TS_SIZE = 40
BROKER_NUMBERS = 5
SHAREHOLDER_NUMBERS = 10
MIN_CREDIT = 50
MAX_CREDIT = 200
MIN_SHARE = 5
MAX_SHARE = 20

upperbound = np.array \
        (
        (
                [1]
                + [MAX_CREDIT] * BROKER_NUMBERS
                + [MAX_SHARE] * SHAREHOLDER_NUMBERS
                + [MAX_PRICE]  # reference price
                + [
                    MAX_TC_SIZE * 3 - 1,  # order ID
                    BROKER_NUMBERS,  # broker ID
                    SHAREHOLDER_NUMBERS,  # shareholder ID
                    MAX_PRICE,  # price
                    MAX_QTY,  # quantity
                    1,  # side (is BUY)
                    MAX_MODAL_QTY,  # minimum quantity
                    1,  # FAK (is FAK)
                    MAX_MODAL_QTY,  # disclosed quantitys
                ] * MAX_TC_SIZE
        ) * MAX_TS_SIZE
    )

lowerbound = np.array \
        (
        (
                [0]
                + [MIN_CREDIT] * BROKER_NUMBERS
                + [MIN_SHARE] * SHAREHOLDER_NUMBERS
                + [0]  # reference price
                + [
                    0,  # order ID
                    1,  # broker ID
                    1,  # shareholder ID
                    0,  # price
                    0,  # quantity
                    0,  # side (is BUY)
                    0,  # minimum quantity
                    0,  # FAK (is FAK)
                    0,  # disclosed quantitys
                ] * MAX_TC_SIZE
        ) * MAX_TS_SIZE
    )

# print(lowerbound)


class ProblemSpecification(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=4280,
            n_obj=2,
            n_constr=0,
            xl=lowerbound,
            xu=upperbound
        )

    def _evaluate(self, x, out, *args, **kwargs):
        decoder = ArrayDecoder(BROKER_NUMBERS, SHAREHOLDER_NUMBERS, ORD_ENCODED_SIZE, MAX_TC_SIZE, MAX_TS_SIZE)
        traces = list(map(lambda tc: tc.traces, decoder.decode_ts(x)))
        ts_size = len(traces)
        # print(x)
        coverage = get_coverage()
        out["F"] = [-int(coverage.expression), ts_size]


algorithm = NSGA2(
    pop_size=100,
    n_offsprings=100,
    sampling=get_sampling("int_random"),
    crossover=get_crossover("int_sbx", prob=0.5, eta=15),
    mutation=get_mutation("int_pm", eta=20),
    eliminate_duplicates=True
)

termination = get_termination("n_gen", 10)
res = minimize(ProblemSpecification(),
               algorithm,
               termination,
               seed=1,
               save_history=True,
               verbose=True)
print(res.opt)
