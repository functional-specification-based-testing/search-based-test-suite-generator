import re
import subprocess
from dataclasses import dataclass, astuple

TMP_FILE_ADDR = "/tmp/wdajdjkposlf-expression"
TRACE_CALC_ADDR = "./GetTCTraces --traces "
TRACE_FEDD_ADDR = "./GetTCTraces --trades "
COVERAGE_ADDR = "hpc report GetTCTraces"
RESET_COVERAGE = "rm GetTCTraces.tix"

WORKING_DIRECTORY = "../haskell-matching-engine/dist"


@dataclass
class Order:
    order_id: ...
    broker_id: ...
    shareholder_id: ...
    price: ...
    qty: ...
    side: ...
    min_qty: ...
    fak: ...
    disclosed_qty: ...


class TestCase:
    def __init__(self, credits, shares, reference_price, ords):
        self.credits = credits
        self.shares = shares
        self.reference_price = reference_price
        self.ords = ords
        self.translated_orders = 0
        self.translated = self._translate()
        self.traces = self._calc_test_case_trace()
        # self.test_case = self.gen_test_case_feed().split("\n")

    @staticmethod
    def _translate_new_ord(order):
        return "NewOrderRq\t%s" % "\t".join([str(spec) for spec in list(astuple(order))[1:]])

    @staticmethod
    def _translate_replace_ord(order, original_id):
        return "ReplaceOrderRq\t%s" % "\t".join([str(spec) for spec in [original_id] + list(astuple(order))[1:]])

    @staticmethod
    def _translate_cancel_ord(order, original_id):
        return "CancelOrderRq\t%s" % "\t".join([str(spec) for spec in [original_id, order.side]])

    @staticmethod
    def _translate_credit(broker, credit):
        return "SetCreditRq\t%d\t%d" % (broker + 1, credit)

    @staticmethod
    def _translate_share(shareholder, share):
        return "SetOwnershipRq\t%d\t%d" % (shareholder + 1, share)

    @staticmethod
    def _translate_reference_price(reference_price):
        return "SetReferencePriceRq\t%d" % (reference_price)

    @staticmethod
    def _translate_static_price_band_upper_limit(limit):
        return "SetStaticPriceBandUpperLimitRq\t%0.2f" % (limit)

    @staticmethod
    def _translate_static_price_band_lower_limit(limit):
        return "SetStaticPriceBandLowerLimitRq\t%0.2f" % (limit)

    @staticmethod
    def _translate_tick_size(price):
        return "SetTickSizeRq\t%d" % (price)

    @staticmethod
    def _translate_lot_size(qty):
        return "SetLotSizeRq\t%d" % (qty)

    @staticmethod
    def _translate_ownership_upper_limit(limit):
        return "SetOwnershipUpperLimitRq\t%0.2f" % (limit)

    @staticmethod
    def _translate_total_shares(shares):
        return "SetTotalSharesRq\t%d" % (shares)

    def _translate_ord(self, order):
        raw_original_id = order.order_id
        original_id = raw_original_id % 3
        if self.translated_orders:
            original_id %= self.translated_orders
        self.translated_orders += 1

        if raw_original_id % 3 == 0:
            return TestCase._translate_new_ord(order)
        elif raw_original_id % 3 == 1:
            return TestCase._translate_replace_ord(order, original_id)
        elif raw_original_id % 3 == 2:
            return TestCase._translate_cancel_ord(order, original_id)

    def _translate(self):
        return "\n".join(sum([
            [TestCase._translate_credit(broker, credit) for (broker, credit) in enumerate(self.credits)],
            [TestCase._translate_share(shareholder, share) for (shareholder, share) in enumerate(self.shares)],
            [TestCase._translate_reference_price(self.reference_price)],
            [TestCase._translate_static_price_band_upper_limit(0.9)],
            [TestCase._translate_static_price_band_lower_limit(0.9)],
            [TestCase._translate_tick_size(1)],
            [TestCase._translate_lot_size(1)],
            [TestCase._translate_ownership_upper_limit(0.2)],
            [TestCase._translate_total_shares(100)],
            [self._translate_ord(order) for order in self.ords],
        ], []))

    # use this when you want to count the number of unique traces generated
    # def _calc_test_case_trace(self):
    #     with open(TMP_FILE_ADDR, 'w') as f:
    #         print(self.translated, file=f)
    #
    #     process = subprocess.Popen(TRACE_CALC_ADDR + TMP_FILE_ADDR, cwd=WORKING_DIRECTORY, shell=True,
    #                                stdout=subprocess.PIPE)
    #     output, error = process.communicate()
    #     return set(output.decode("utf-8").split())

    def _calc_test_case_trace(self):
        with open(TMP_FILE_ADDR, 'w') as f:
            print(self.translated, file=f)

        process = subprocess.Popen(TRACE_CALC_ADDR + TMP_FILE_ADDR, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        output, error = process.communicate()
        data_flow_coverage = [df for df in output.split(b' ') if df.find(b'DF') != -1 and b'tau' not in df]
        # data_flow_coverage = []
        # print(output)
        # for df in output.split(b' '):
        #     print(df)
        #     if df.find(b'DF') != -1:
        #         if b'tau' not in df:
        #             print("found a match")
        #             data_flow_coverage.append(df)
        print(data_flow_coverage)
        du_paths = 0
        credit_def = False
        ownership_def = False
        for item in data_flow_coverage:
            if item == b'DF-D-credit':
                credit_def = True
            elif item == b'DF-U-credit' and credit_def:
                credit_def = False
                du_paths += 1
            elif item == b'DF-D-ownership':
                ownership_def = True
            elif item == b'DF-U-ownership' and ownership_def:
                ownership_def = False
                du_paths += 1
        print("du_path count: " + str(du_paths))
        return du_paths

    def gen_test_case_feed(self):
        with open(TMP_FILE_ADDR, 'w') as f:
            print(self.translated, file=f)

        process = subprocess.Popen(TRACE_FEDD_ADDR + TMP_FILE_ADDR, cwd=WORKING_DIRECTORY, shell=True,
                                   stdout=subprocess.PIPE)
        output, error = process.communicate()
        return output.decode("utf-8")

    def __repr__(self):
        return self.translated + "\n" + str(self.traces)


class ArrayDecoder:
    def __init__(self, broker_numbers, shareholder_numbers, ord_encoded_size, max_tc_size, max_ts_size):
        self.broker_numbers = broker_numbers
        self.shareholder_numbers = shareholder_numbers
        self.ord_encoded_size = ord_encoded_size
        self.max_tc_size = max_tc_size
        self.max_ts_size = max_ts_size
        self.tc_encoded_size = 1 + broker_numbers + shareholder_numbers + 1 + max_tc_size * ord_encoded_size

    def is_order_valid(self, order):
        if (
                order.price == 0
                or order.qty == 0
                or order.min_qty > order.qty
                or order.disclosed_qty > order.qty
        ):
            return False
        if order.disclosed_qty > 0 and order.fak:
            return False
        return True

    def decode_tc(self, tc_encoded):
        credits = tc_encoded[:self.broker_numbers]
        shares = tc_encoded[self.broker_numbers:self.shareholder_numbers + self.broker_numbers]
        reference_price = tc_encoded[self.shareholder_numbers + self.broker_numbers]
        ords_encoded = tc_encoded[self.shareholder_numbers + self.broker_numbers + 1:]
        ords = []
        for j in range(self.max_tc_size):
            order = Order(*[int(spec)
                            for spec in ords_encoded[j * self.ord_encoded_size:(j + 1) * self.ord_encoded_size]])
            order.side = order.side == 1
            order.fak = order.fak == 1
            if not self.is_order_valid(order):
                continue
            ords.append(order)
        if len(ords) > 0:
            return TestCase(credits, shares, reference_price, ords)
        return None

    def decode_ts(self, ts_encoded):
        # process = subprocess.Popen(RESET_COVERAGE, cwd=WORKING_DIRECTORY, shell=True, stdout=subprocess.PIPE)
        # output, error = process.communicate()
        # if error:
        #     errors = open("errors.txt", "a")
        #     errors.write(str(error) + "\n")
        ts = []
        for i in range(self.max_ts_size):
            is_in_idx = i * self.tc_encoded_size
            ts_encoded[is_in_idx] = ts_encoded[is_in_idx] == 1
            if not ts_encoded[is_in_idx]:
                continue
            tc_encoded = ts_encoded[
                         i * self.tc_encoded_size + 1:(i + 1) * self.tc_encoded_size
                         ]
            tc = self.decode_tc(tc_encoded)
            if tc is not None:
                ts.append(tc)
        return ts


class Coverage:
    branch: ...
    expression: ...
    statement: ...


def get_coverage():
    coverage = Coverage()
    process = subprocess.Popen(COVERAGE_ADDR, cwd=WORKING_DIRECTORY, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    bc = re.findall(r"(\d+)% boolean", str(output))
    coverage.branch = bc[0]
    ec = re.findall(r"(\d+)% expressions", str(output))
    coverage.expression = ec[0]
    sc = re.findall(r"(\d+)% alternatives", str(output))
    coverage.statement = sc[0]
    # print(vars(coverage).items())
    return coverage


def gen_test_suite_feed(ts):
    return "\n".join([
        str(len(ts)),
        "".join(map(lambda tc: tc.gen_test_case_feed(), ts)),
    ])


def save_test_suite_feed(ts, addr):
    with open(addr, "w") as f:
        f.write(gen_test_suite_feed(ts))
