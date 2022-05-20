from main import Testcase, Command


def calculate_isp(testcase: Testcase):
    testcase_orders = testcase.get_all_orders()
    testcase_trades = testcase.get_all_trades()
    testcase_queue = testcase.get_final_queue()

    isps = {'p1_1_isp': False,
            'p1_2_isp': False,
            'p1_3_isp': False,
            'p1_4_isp': False,
            'p1_5_isp': False,
            'p2_1_isp': False,
            'p2_2_isp': False,
            'p2_3_isp': False,
            'p3_1_isp': False,
            'p3_2_isp': False,
            'p3_3_isp': False
            }

    for order in testcase_orders:
        trade_count = 0
        final_quantity = 0
        for trade in testcase_trades:
            if order.order_id == trade.buy_id or order.order_id == trade.sell_id:
                if order.quantity == trade.quantity:
                    isps['p1_1_isp'] = True
                elif order.quantity < trade.quantity:
                    isps['p1_2_isp'] = True
                elif order.quantity > trade.quantity:
                    trade_count += 1
                    final_quantity += trade.quantity

        if trade_count > 1 and final_quantity == order.quantity:
            isps['p1_3_isp'] = True
        elif trade_count == 0:
            isps['p1_4_isp'] = True
        elif trade_count > 0 and final_quantity < order.quantity:
            isps['p1_5_isp'] = True

        if not isps['p2_2_isp'] and not testcase_queue:
            isps['p2_2_isp'] = True
        for in_queue in testcase_queue:
            if not isps['p2_1_isp'] and\
                    order.order_id == in_queue.order_id and order.quantity == in_queue.quantity:
                isps['p2_1_isp'] = True
            elif not isps['p2_3_isp'] and\
                    order.order_id == in_queue.order_id and order.quantity > in_queue.quantity:
                isps['p2_3_isp'] = True

        if not isps['p3_1_isp'] and\
                order.min_quantity == order.quantity:
            isps['p3_1_isp'] = True
        elif not isps['p3_2_isp'] and\
                0 < order.min_quantity < order.quantity:
            isps['p3_2_isp'] = True
        elif not isps['p3_3_isp'] and\
                order.min_quantity == 0:
            isps['p3_3_isp'] = True

    return isps
