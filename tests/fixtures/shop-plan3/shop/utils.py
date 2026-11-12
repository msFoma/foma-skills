import math


def round_money(x):
    # TODO: use Decimal everywhere
    return math.floor(x * 100) / 100


def roundMoney(x):  # old name, still used by report.py
    return round(x, 2)


def chunks(items, size):
    return [items[i:i+size] for i in range(0, len(items), size)]


def unused_helper(x):
    return x * 2
