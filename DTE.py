# DTE.py

# Implementation of the distribution transforming encoder (DTE)
# using the API for a message space described in probabilityfunctionAPI.py

import random
import probabilityfunctionAPI

# Define length of seed space
SEED_SPACE_LENGTH = 64
seed_space = 2**SEED_SPACE_LENGTH - 1

"""
Takes in a message and a MessageSpaceProbabilityFxns object
and returns a corresponding random bit string in
the seed space.
"""
def encode(m, pfxns):
    check = str(luhn(m[:-1]))
    if check != m:
        print('Invaid Card Number!')
        return -1
    if pfxns.prob_distr(m) == 0:
        return -1
    # get range of seed space to pick random string from
    print('True seed probability location: ', pfxns.cumul_distr(m))
    start = pfxns.cumul_distr(m) * seed_space
    end = int(start + pfxns.prob_distr(m)*seed_space) - 1 
    start = int(start)

    # pick random string from corresponding seed space
    seed = int(random.random() * (end-start) + start)
    return seed

"""
Takes in an ordered table [(value, msg)] and a value to search for in the table.
Returns the highest index message in the table that is less than the inputted value.
Initial call : binary_search(table, 0, len(table), value)
"""
def binary_search(table, start, end, value):
    size = end - start
    # base case
    if size == 1 or size == 0:
        return table[start]
    
    mid = start + size//2

    (mid_value, mid_msg) = table[mid]
    # recursion step
    if value >= mid_value:
        return binary_search(table, mid, end, value)
    else:
        return binary_search(table, start, mid, value)
    

"""
Takes in a seed and a MessageSpaceProbabilityFxns object and
runs binary search on pre-calculated inverse sampling table and linear
search to find corresponding message.
"""
def decode(s, pfxns):
    table = pfxns.get_inverse_cumul_distr_samples()
    seed_loc = float(s)/seed_space
    print('Guessed seed probability location: ', seed_loc)
    _, prev_msg = binary_search(table, 0, len(table), seed_loc)
    next_msg = pfxns.next_message(prev_msg)
    next_value = pfxns.cumul_distr(next_msg)
    if next_msg == prev_msg: # at max message
        return prev_msg
    # begin linear scan to find which range seed s falls in
    while seed_loc >= next_value:
        # update prev and next
        _, prev_msg = (next_value, next_msg)
        next_msg = pfxns.next_message(prev_msg)
        next_value = pfxns.cumul_distr(next_msg)
    
    return prev_msg

from probabilityfunctionAPI import MessageSpaceProbabilityFxns
import math

# helper function to get denominator of prefix probabilities
def getTotalProbability(prefixes):
    sum = 0
    for _,val in prefixes.items():
        sum += val[2]
    return sum

"""
Creates prefix cumulative probability distribution
"""
def create_cumul_fxn(prefix_order, prefixes, total_prob):
    cumul_prob = 0
    prefix_cumul = {}
    for prefix in prefix_order:
        prefix_cumul[prefix] = cumul_prob
        cumul_prob += float(prefixes[prefix][2]) / total_prob
    return prefix_cumul

"""
Creates list of ordered prefixes
"""
def create_prefix_ordered_list(prefixes):
    return sorted(prefixes,key = prefixes.get)

"""
Create inverse sampling table
"""
def create_inverse_sample_table():
    with open('inverse_table.txt','r') as f:
        table = eval(f.read())
    return table

# given random message string as int, return int message with last digit appended such that new string is Luhn-valid
def luhn(m):
    sum = 0
    for parity, i in enumerate(list(str(m))):
        if parity%2 == 0:
            num = int(i)
            sum += (num*2)//10 + (num*2)%10 if num*2 >= 10 else num*2
        else:
            sum += int(i)
    last = (9 * sum) % 10
    return int(m) * 10 + last

class CreditCardProbabilityFxns(MessageSpaceProbabilityFxns):

    def __init__(self, prefixes):
        self.prefixes = prefixes
        self.prefix_order = create_prefix_ordered_list(prefixes)
        self.total_prob = getTotalProbability(prefixes)
        self.prefix_cumul = create_cumul_fxn(self.prefix_order, prefixes, self.total_prob)
        self.inverse_table = create_inverse_sample_table()


        # define probability distribution fxn
        # this actually doesn't depend on the prefix but only the length of the string....
        # whatever
        def prob(self, m):
            prefix = list('******')
            for i in range(6):
                prefix[i] = m[i]
                prefixStr = ''.join(prefix)
                if prefixStr in self.prefixes:
                    prefixProb = 1.0 / self.total_prob
                    #last digit is the check dig
                    randomDigs = m[6:-1]
                    numRandomDigs = len(randomDigs)
                    prob = prefixProb * math.pow(10,-numRandomDigs)
                    return prob
            print ("Credit card not in list")
            return 0

        # define cumul distribution fxn
        def cumul(self, m):
            #print (m)
            prefix = list('******')
            for i in range(6):
                prefix[i] = m[i]
                prefixStr = ''.join(prefix)
                if prefixStr in self.prefixes:
                    #last digit is the check dig
                    randomDigs = m[6-self.prefixes[prefixStr][0]:-1]
                    numRandomDigs = self.prefixes[prefixStr][1] - 7
                    prefixCumul = self.prefix_cumul[prefixStr]
                    totalCumul = prefixCumul + float(randomDigs)*pow(10,-numRandomDigs) / self.total_prob
                    return totalCumul
            print ("Invalid credit card")
            return -1

        # define next message fxn
        # simplified to never carry over to another prefix
        def next_msg(self,m):
            baseNumber = int(m[:-1])
            return str(luhn(baseNumber+1))

        # create get sample table
        def get_inverse_table(self):
            return self.inverse_table


        # Initialize MessageSpaceProbabilityFxns
        MessageSpaceProbabilityFxns.__init__(self, cumul, prob, next_msg, get_inverse_table)