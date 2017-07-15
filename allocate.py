import math
from random import shuffle

### KNOBS ###

# How many shares to "back-off" from the naive starting allocation
STARTING_BACKOFF = 1;
# How much over the golden allocation is too much to warrent continuing
OVER_ALLOCATION_THRESHOLD = 1.05

# GLOBALS
PRICES = {"VTI":126.23, "VEA":42.07, "VWO":42.52, "VIG":93.49, "VNQ":83.08, "VCIT":87.7, "VWOB":80.04}
TARGET_PERCENTAGES = {"VTI":0.21, "VEA":0.18, "VWO":0.22, "VIG":0.13, "VNQ":0.16, "VCIT":0.05, "VWOB":0.05, "cash":0}
TOTAL_CASH = 19205.71
PERFECT_AMOUNTS = {k: TOTAL_CASH*TARGET_PERCENTAGES.get(k) for k in TARGET_PERCENTAGES.keys() }
SEEN_STATES = set()
BEST_SO_FAR = {"best":{}}

def main():
    allocations = get_starting_allocations(PERFECT_AMOUNTS)
    BEST_SO_FAR["best"] = allocations.copy()
    allocate(allocations)
    print_result(BEST_SO_FAR["best"])

def allocate(allocations):
    purchase_options = get_possisible_purchases(allocations["cash"])
    if not purchase_options:
        current_avg_delta = get_avg_delta(allocations)
        best_so_far_delta = get_avg_delta(BEST_SO_FAR["best"])
        if (current_avg_delta < best_so_far_delta):
            print "Best deviation so far " + str(current_avg_delta) + " ..."
            BEST_SO_FAR["best"] = allocations.copy()
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

def get_avg_delta(allocations):
    total = 0;
    for asset, value in allocations.iteritems():
        if asset == "cash":
            total += allocations["cash"]
        else:
            total += abs(PERFECT_AMOUNTS[asset] - (allocations[asset] * PRICES[asset]))
    return total/len(allocations)

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
    print "================================================="
    print "                OPTIMAL ALLOCATION"
    print "================================================="
    print "|\tSYM\t|\tSHARES\t|\tTOTAL\t|"
    print "-------------------------------------------------"
    total = 0;
    for symbol, shares in allocations.iteritems():
        if not symbol == "cash":
            this_amount = round(PRICES[symbol]*shares, 2);
            total += this_amount
            print "|\t" + str(symbol) + "\t|\t" + str(shares) + "\t|\t" + str(this_amount) + "\t|"
    print "|\tCASH\t|\t\t|\t" + str(TOTAL_CASH - total) + "\t|"
    print "-------------------------------------------------"
    


if __name__ == "__main__": main()
