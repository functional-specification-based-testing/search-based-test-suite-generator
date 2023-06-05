#!/usr/bin/env python3

from haskell_adaptor import ArrayDecoder, get_coverage, save_test_suite_feed

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


decoder = ArrayDecoder(BROKER_NUMBERS, SHAREHOLDER_NUMBERS, ORD_ENCODED_SIZE, MAX_TC_SIZE, MAX_TS_SIZE)
file = open("run-temp.txt", "r")
x = file.readline().split(", ")
# traces = list(map(lambda tc: tc.traces, decoder.decode_ts(x)))
# ts = decoder.decode_ts(x)
for i in range(len(x)):
    if i % 107 == 0:
        print(x[i])
# print(str(len(ts)))
# save_test_suite_feed(x, "temp-traces")

# coverage = get_coverage()
