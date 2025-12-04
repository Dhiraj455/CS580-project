import problem1

def naive_line_join(list_of_relations):
    """
    Evaluates R1 ⨝ R2 ⨝ ... ⨝ Rk sequentially using hash joins.
    Input: list of relations [R1, R2, ..., Rk] where each R_i has 2 attributes
           and joins as R1(A1,A2) ⨝ R2(A2,A3) ⨝ ... ⨝ Rk(Ak,Ak+1)
    Returns: list of result tuples after the join
    """
    # Start with the first relation as the accumulated result
    current_result = list_of_relations[0]
    
    # Iteratively join with the next relation in the list
    for i in range(1, len(list_of_relations)):
        next_relation = list_of_relations[i]
        
        # Apply the Hash Join function from Problem 1
        current_result = problem1.hash_join(current_result, next_relation)
        
    return current_result

def problem_3_solution():
    # ==========================================
    # Test Data (Same as Problem 2 for consistency)
    # ==========================================
    # R1(A, B)
    R1 = [(1, 100), (2, 100), (9, 999)]
    # R2(B, C)
    R2 = [(100, 20), (100, 21), (888, 55)]
    # R3(C, D)
    R3 = [(20, 5), (21, 6), (33, 7)]

    print("--- Problem 3: Naive Line Join ---")
    all_relations = [R1, R2, R3]
    
    # Run the algorithm
    final_output = naive_line_join(all_relations)
    
    print(f"Final Result Count: {len(final_output)}")
    for row in final_output:
        print(row)

if __name__ == "__main__":
    problem_3_solution()