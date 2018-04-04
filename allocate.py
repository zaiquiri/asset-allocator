import urllib
import re
import math
import sys

### KNOBS ###

### ---PERFORMANCE--- ###
# How many shares to "back-off" from the naive starting allocation
STARTING_BACKOFF = 2;
# How much over the golden allocation is too much to warrent continuing
OVER_ALLOCATION_THRESHOLD = 1.05
### ---ACCURACY--- ###
# How much over/under target allocation can still be considered "perfect"
ALLOCATION_TOLERANCE = 0
# How important not having leftover cash is
CASH_WEIGHT = 1

def get_securities():
    return ["VTI", "VEA", "VWO", "VIG", "VNQ", "VCIT", "VWOB"]

def get_targets():
    return {"VTI":0.23, "VEA":0.19, "VWO":0.17, "VIG":0.15, "VNQ":0.15, "VCIT":0.05, "VWOB":0.06, "cash":0}

def get_current_holdings():
    return {"VTI":31.268, "VEA":76.985, "VWO":67.95, "VIG":28.25, "VNQ":31.747, "VCIT":10.136, "VWOB":13.255}

def get_total_cash():
    return 23990.96

PRICES = {"VTI": 141.81, "VEA": 46.21 , "VWO": 48.47, "VIG": 105.30, "VNQ": 76.57, "VCIT": 85.54, "VWOB": 79.10}
PERFECT_AMOUNTS = {k: get_total_cash()*get_targets().get(k) for k in get_targets().keys() }
SEEN_STATES = set()
BEST_SO_FAR = [None]
BEST_DISTANCE = [sys.maxint]

def main():
    allocations = get_starting_allocations(PERFECT_AMOUNTS)
    BEST_SO_FAR[0] = allocations.copy()
    is_better(BEST_SO_FAR[0])
    allocate(allocations)
    print_result(BEST_SO_FAR[0])
    print_instructions(BEST_SO_FAR[0])

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
    cash = get_total_cash();
    for asset, amount in perfect_amounts.iteritems():
        if not asset == "cash":
            decimal_part = get_current_holdings()[asset] - math.floor(get_current_holdings()[asset])
            allocations[asset] = math.floor(perfect_amounts[asset] / PRICES[asset]) - STARTING_BACKOFF + decimal_part
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
            print "|\t" + str(symbol) + "\t|\t" + str(shares) + "\t|\t" + str(get_targets()[symbol]) + "\t|\t" + str(round(this_amount/get_total_cash(), 4)) + "\t|\t" + str(this_amount) + "\t|"
    print "|\tCASH\t|\t\t|\t0.00\t|\t" + str(round((get_total_cash() - total)/get_total_cash(), 2)) + "\t|\t" + str(get_total_cash() - total) + "\t|"
    print "---------------------------------------------------------------------------------"

def print_instructions(allocations):
    current_holdings = get_current_holdings()
    for symbol, desired_shares in allocations.iteritems():
        if not symbol == "cash":
            diff = desired_shares - current_holdings[symbol]
            if (diff < 0):
                print "SELL " + symbol + ": " + str(abs(diff))
            if (diff > 0):
                print "BUY " + symbol + ": " + str(diff)

if __name__ == "__main__": main()
