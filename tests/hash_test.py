import math

def hash_overlap_prob(num_elements, num_possible_values):
    numerator = 1
    
    for i in range(num_possible_values, num_possible_values - num_elements, -1):
        numerator *= i
    
    denominator = num_possible_values ** num_elements

    prob_overlap = 1 - (numerator / denominator)
    return prob_overlap

num_elements = 65000
num_possible_values = 10**10

prob_overlap = hash_overlap_prob(num_elements, num_possible_values)

print(f"with {num_elements} elements being hashed into {num_possible_values} possible values, prob overlap is {prob_overlap:.10f}")
