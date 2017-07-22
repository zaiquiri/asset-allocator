import math
import sys
from random import shuffle

### KNOBS ###

### ---PERFORMANCE--- ###
# How many shares to "back-off" from the naive starting allocation
STARTING_BACKOFF = 2;
# How much over the golden allocation is too much to warrent continuing
OVER_ALLOCATION_THRESHOLD = 1.05
### ---ACCURACY--- ###
# How much over/under target allocation can still be considered "perfect"
ALLOCATION_TOLERANCE = .025
# How important not having leftover cash is
CASH_WEIGHT = 12

# GLOBALS
PRICES = {"VTI":126.31, "VEA":42.09, "VWO":42.37, "VIG":93.36, "VNQ":83.57, "VCIT":88, "VWOB":80.23}
TARGET_PERCENTAGES = {"VTI":0.21, "VEA":0.18, "VWO":0.22, "VIG":0.13, "VNQ":0.16, "VCIT":0.05, "VWOB":0.05, "cash":0}
TOTAL_CASH = 19205.71
PERFECT_AMOUNTS = {k: TOTAL_CASH*TARGET_PERCENTAGES.get(k) for k in TARGET_PERCENTAGES.keys() }
SEEN_STATES = set()
BEST_SO_FAR = [None]
BEST_DISTANCE = [sys.maxint]

def main():
    allocations = get_starting_allocations(PERFECT_AMOUNTS)
    BEST_SO_FAR[0] = allocations.copy()
    is_better(BEST_SO_FAR[0])
    allocate(allocations)
    print_result(BEST_SO_FAR[0])

def allocate(allocations):
    purchase_options = get_possisible_purchases(allocations["cash"])
    if not purchase_options:
        if (is_better(allocations)):
            print allocations
            BEST_SO_FAR[0] = allocations.copy()
    else:
        for purchase in purchase_options:
            add_purchase(purchase, allocations)
            if not seen_combination(allocations) and not gratutitous_allocation(purchase, allocations):
                allocate(allocations)
            remove_purchase(purchase, allocations)

def get_possisible_purchases(cash):
    possisible_purchases = []
    for symbol, price in PRICES.iteritems():
        if (cash - price >= 0):
            possisible_purchases.append(symbol)
    return possisible_purchases

def is_better(allocations):
    total_dollars_from_perfect = 0;
    uninvested_cash = allocations["cash"]
    for asset, value in allocations.iteritems():
        if not asset == "cash":
            dollars_from_perfect = abs(PERFECT_AMOUNTS[asset] - PRICES[asset]*allocations[asset])
            total_dollars_from_perfect += dollars_from_perfect if (dollars_from_perfect/PERFECT_AMOUNTS[asset]) > ALLOCATION_TOLERANCE else 0
    distance_from_perfect = math.sqrt((uninvested_cash*CASH_WEIGHT)**2 + total_dollars_from_perfect**2)
    if (distance_from_perfect < BEST_DISTANCE[0]):
        print "DIST: " + str(distance_from_perfect)
        BEST_DISTANCE[0] = distance_from_perfect
        return True
    return False

def add_purchase(purchase_symbol, allocations):
    allocations[purchase_symbol] += 1;
    allocations["cash"] -= PRICES[purchase_symbol]

def remove_purchase(purchase_symbol, allocations):
    allocations[purchase_symbol] -= 1;
    allocations["cash"] += PRICES[purchase_symbol]

def seen_combination(allocations):
    test = allocations.copy()
    test["cash"] = round(test["cash"], 2)
    if (frozenset(test.items()) in SEEN_STATES):
        return True
    else:
        SEEN_STATES.add(frozenset(test.items()))
        return False;

def gratutitous_allocation(purchase, allocations):
    return allocations[purchase] * PRICES[purchase] / PERFECT_AMOUNTS[purchase] > OVER_ALLOCATION_THRESHOLD

def get_starting_allocations(perfect_amounts):
    allocations = {}
    cash = TOTAL_CASH;
    for asset, amount in perfect_amounts.iteritems():
        if not asset == "cash":
            allocations[asset] = math.floor(perfect_amounts[asset] / PRICES[asset]) - STARTING_BACKOFF
            cash -= allocations[asset] * PRICES[asset]
    allocations["cash"] = cash
    return allocations

def print_result(allocations):
    print "================================================================================="
    print "                                 OPTIMAL ALLOCATION"
    print "================================================================================="
    print "|\tSYM\t|\tSHARES\t|\tTARGET\t|\tACTUAL\t|\tTOTAL\t|"
    print "---------------------------------------------------------------------------------"
    total = 0;
    for symbol, shares in allocations.iteritems():
        if not symbol == "cash":
            this_amount = round(PRICES[symbol]*shares, 2);
            total += this_amount
            print "|\t" + str(symbol) + "\t|\t" + str(shares) + "\t|\t" + str(TARGET_PERCENTAGES[symbol]) + "\t|\t" + str(round(this_amount/TOTAL_CASH, 4)) + "\t|\t" + str(this_amount) + "\t|"
    print "|\tCASH\t|\t\t|\t0.00\t|\t" + str(round((TOTAL_CASH - total)/TOTAL_CASH, 2)) + "\t|\t" + str(TOTAL_CASH - total) + "\t|"
    print "---------------------------------------------------------------------------------"
    


if __name__ == "__main__": main()
