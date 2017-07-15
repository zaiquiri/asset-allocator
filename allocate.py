import math

PRICES = {"VTI":126.23, "VEA":42.07, "VWO":42.52, "VIG":93.49, "VNQ":83.08, "VCIT":87.7, "VWOB":80.04}
TARGET_PERCENTAGES = {"VTI":0.21, "VEA":0.18, "VWO":0.22, "VIG":0.13, "VNQ":0.16, "VCIT":0.05, "VWOB":0.05, "cash":0}
TOTAL_CASH = 19205.71
PERFECT_AMOUNTS = {k: TOTAL_CASH*TARGET_PERCENTAGES.get(k) for k in TARGET_PERCENTAGES.keys() }
SEEN_STATES = set()

def main():
    allocations = get_starting_allocations(PERFECT_AMOUNTS)
    best_so_far = allocations
    allocate(allocations, best_so_far)
    print best_so_far

def allocate(allocations, best_so_far):
    purchase_options = get_possisible_purchases(allocations["cash"])
    if not purchase_options:
        if (get_avg_delta(allocations) < get_avg_delta(best_so_far)):
            print "found better"
            best_so_far = allcoations.copy()
    else:
        for purchase in purchase_options:
            add_purchase(purchase, allocations)
            if not seen_combination(allocations) and not gratutitous_allocation(purchase, allocations):
                allocate(allocations, best_so_far)
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
    if (frozenset(allocations.items()) in SEEN_STATES):
        return True
    else:
        SEEN_STATES.add(frozenset(allocations.items()))
        return False;

def gratutitous_allocation(purchase, allocations):
    return allocations[purchase] * PRICES[purchase] / PERFECT_AMOUNTS[purchase] > 1.05

def get_starting_allocations(perfect_amounts):
    allocations = {}
    optimization_buffer = 2
    cash = TOTAL_CASH;
    for asset, amount in perfect_amounts.iteritems():
        if not asset == "cash":
            allocations[asset] = math.floor(perfect_amounts[asset] / PRICES[asset]) - optimization_buffer
            cash -= allocations[asset] * PRICES[asset]
    allocations["cash"] = cash
    return allocations

if __name__ == "__main__": main()
