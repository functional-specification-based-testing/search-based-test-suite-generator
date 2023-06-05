#!/usr/bin/env python3
import pathlib

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.factory import get_termination
from pymoo.optimize import minimize

from haskell_adaptor import ArrayDecoder, get_coverage, save_test_suite_feed, gen_test_suite_feed
from main import Testcase, check_all_isps, isp_list
from isp_coverage import calculate_isp

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


decoder = ArrayDecoder(BROKER_NUMBERS, SHAREHOLDER_NUMBERS, ORD_ENCODED_SIZE, MAX_TC_SIZE, MAX_TS_SIZE)


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

        test_suite = decoder.decode_ts(x)
        coverage = get_coverage()

        isps = {}
        for testcase in test_suite:
            test_case = Testcase()
            test_case.parse(testcase.test_case)
            isps = calculate_isp(test_case)
        score = sum(1 for c in isps.values() if c)

        out["F"] = [-int(coverage.expression), -score]
        # out["G"] = [11 - score]

        # try:
        # traces = list(map(lambda tc: tc.traces, decoder.decode_ts(x)))
        # ts_size = len(traces)
        # print("##############################################################")
        # print(traces)
        # print("------------------------------------------------------------------------")

        # isp_dic = {}
        # for isp in isp_list:
        #     isp_dic[isp.__name__] = False
        #
        # test_suite = decoder.decode_ts(x)
        # for case in test_suite:
        #     testcase = case.gen_test_case_feed().split("\n")
        #     print(case.test_case)
        # print("---------------------------")
        # test_case = Testcase()
        # test_case.parse(case.test_case)
        # isps = check_all_isps(test_case)
        # for key, value in isp_dic.items():
        #     isp_dic[key] = isps[key] | value
        # score = sum(1 for c in isp_dic.values() if c)
        # print(score)

        # out["F"] = [-score]
        # print(score)

        # if ts_size == 0:
        #     out["F"] = [1, 1]
        # out["F"] = [1]
        # else:
        #     coverage = get_coverage()
        #     out["F"] = [-int(coverage.expression), -score]
        # out["F"] = [-int(coverage.expression)]
    # except BaseException as error:
    #     with open("run-temp.txt", "w") as file:
    #         file.write(", ".join(str(item) for item in x))
    #         file.write("-----------------------------------------------------------------------------------\n")
    #     print(error)


algorithm = NSGA2(
    pop_size=100,
    n_offsprings=100,
    sampling=get_sampling("int_random"),
    crossover=get_crossover("int_sbx", prob=0.5, eta=15),
    mutation=get_mutation("int_pm", eta=20),
    eliminate_duplicates=True
)

termination = get_termination("n_gen", 20)
res = minimize(ProblemSpecification(),
               algorithm,
               termination,
               seed=1,
               save_history=True,
               verbose=True)

pathlib.Path("nsga2/").mkdir(parents=True, exist_ok=True)
for i in range(len(res.X)):
    ts = decoder.decode_ts(res.X[i])
    print(str(i) + str(res.F[i]))
    save_test_suite_feed(ts, "nsga2/nsga2-" + str(i) + ".out")
