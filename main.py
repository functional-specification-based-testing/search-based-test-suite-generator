NEW_ORDER_REQ = 'NewOrderRq'
BUY_TYPE = 'BUY'
SELL_TYPE = 'SELL'
TRADE_CMD = 'Trade'
ORDER_QUEUE = 'Order'


class Testcase:
    all_commands: list = []

    def parse(self, lines):
        for line in lines:
            if line.isspace() or line == '':
                continue
            new_command = Command()
            new_command.create_command(line)
            self.all_commands.append(new_command)

    def get_all_orders(self):
        all_orders = []
        for cmd in self.all_commands:
            if cmd.is_order:
                all_orders.append(cmd)
        return all_orders

    def get_all_trades(self):
        all_trades = []
        for cmd in self.all_commands:
            if cmd.is_trade:
                all_trades.append(cmd)
        return all_trades

    def get_final_queue(self):
        final_queue = []
        last_orders_idx = None
        for cmd_idx in range(len(self.all_commands)):
            if self.all_commands[cmd_idx].command == 'Orders':
                last_orders_idx = cmd_idx

        if not last_orders_idx:
            return None

        for cmd_idx in range(last_orders_idx, len(self.all_commands)):
            cmd = self.all_commands[cmd_idx]
            if cmd.is_in_queue:
                final_queue.append(cmd)
        return final_queue


class Command:
    command = None
    args = None
    is_order = False
    is_in_queue = False
    is_trade = False
    order_type = None

    def create_command(self, line_command):

        self.command, *self.args = line_command.split()
        if self.command == NEW_ORDER_REQ or self.command == ORDER_QUEUE:
            if self.command == NEW_ORDER_REQ:
                self.is_order = True
            else:
                self.is_in_queue = True

            self.order_type, self.order_id, self.broker_id, self.shareholder_id, self.price, \
            self.quantity, self.side, self.min_quantity, \
            self.is_fak, self.peak_size = self.args

            self.quantity = int(self.quantity)
            self.min_quantity = int(self.min_quantity)
            self.price = int(self.price)

        elif self.command == TRADE_CMD:
            self.is_trade = True
            self.price, self.quantity, self.buy_id, self.sell_id = self.args

            self.quantity = int(self.quantity)
            self.price = int(self.price)

    def __str__(self) -> str:
        if self.is_order:
            return f'is order: args: {str(self.args)}'

        if self.is_trade:
            return f'is trade: args: {str(self.args)}'

        if self.is_in_queue:
            return f'is in Q: args: {str(self.args)}'

        return f'other cmds: args: {str(self.args)}'


# p1-1: Order match completely with another order
# what about replace order?
def p1_1_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()
    test_case_trades = testcase.get_all_trades()

    for order in test_case_orders:
        for trade in test_case_trades:
            if order.order_id == trade.buy_id or order.order_id == trade.sell_id:
                if order.quantity == trade.quantity:
                    return True

    return False


def p1_2_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()
    test_case_trades = testcase.get_all_trades()

    for order in test_case_orders:
        for trade in test_case_trades:
            if order.order_id == trade.buy_id or order.order_id == trade.sell_id:
                if order.quantity < trade.quantity:
                    return True

    return False


def p1_3_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()
    test_case_trades = testcase.get_all_trades()

    for order in test_case_orders:
        trade_count = 0
        final_quantity = 0
        for trade in test_case_trades:
            if order.order_id == trade.buy_id or order.order_id == trade.sell_id:
                if order.quantity > trade.quantity:
                    trade_count += 1
                    final_quantity += trade.quantity

        if trade_count > 1 and final_quantity == order.quantity:
            return True

    return False


def p1_4_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()
    test_case_trades = testcase.get_all_trades()

    for order in test_case_orders:
        trade_count = 0
        for trade in test_case_trades:
            if order.order_id == trade.buy_id or order.order_id == trade.sell_id:
                trade_count = + 1

        if trade_count == 0:
            return True

    return False


def p1_5_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()
    test_case_trades = testcase.get_all_trades()

    for order in test_case_orders:
        trade_count = 0
        final_quantity = 0
        for trade in test_case_trades:
            if order.order_id == trade.buy_id or order.order_id == trade.sell_id:
                if order.quantity > trade.quantity:
                    trade_count += 1
                    final_quantity += trade.quantity

        if trade_count > 0 and final_quantity < order.quantity:
            return True

    return False


def p2_1_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()
    test_case_final_queue = testcase.get_final_queue()

    for order in test_case_orders:
        for in_queue in test_case_final_queue:
            if order.order_id == in_queue.order_id and order.quantity == in_queue.quantity:
                return True

    return False


def p2_2_isp(testcase: Testcase):
    test_case_final_queue = testcase.get_final_queue()
    return True if not test_case_final_queue else False


def p2_3_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()
    test_case_final_queue = testcase.get_final_queue()

    for order in test_case_orders:
        for in_queue in test_case_final_queue:
            if order.order_id == in_queue.order_id and order.quantity > in_queue.quantity:
                # print('p2_3:', order)
                return True

    return False


def p3_1_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()

    for order in test_case_orders:
        if order.min_quantity == order.quantity:
            return True

    return False


def p3_2_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()

    for order in test_case_orders:
        if 0 < order.min_quantity < order.quantity:
            return True

    return False


def p3_3_isp(testcase: Testcase):
    test_case_orders = testcase.get_all_orders()

    for order in test_case_orders:
        if order.min_quantity == 0:
            return True

    return False


isp_list = [p1_1_isp, p1_2_isp, p1_3_isp, p1_4_isp, p1_5_isp, p2_1_isp,
            p2_2_isp, p2_3_isp, p3_1_isp, p3_2_isp, p3_3_isp]


def check_all_isps(tc, isps=isp_list):
    dic ={}
    for isp in isps:
        dic[isp.__name__] = isp(tc)
        # print(isp.__name__, ':', isp(tc))
        # print(isp(tc))
    return dic


# a = int(input())
# t = Testcase()
# print(f'Test Case: {a}')
# f = open(f'/home/ghazal/Documents/9th_semester/project/inp_isp/3/model/{a}', 'r')
# r = f.readlines()
# t.parse(r)
# check_all_isps(t, isp_list)
