import problem1

def apply_semijoin(left_rel, right_rel, left_col, right_col):
    """
    Performs: left_rel = left_rel SEMIJOIN right_rel
    Filter left_rel to keep only tuples that find a match in right_rel.
    """
    # 1. Build Index of Right Relation keys (Set for O(1) lookup)
    valid_keys = set()
    for t in right_rel:
        valid_keys.add(t[right_col])
        
    # 2. Filter Left Relation
    reduced = []
    for t in left_rel:
        if t[left_col] in valid_keys:
            reduced.append(t)
    return reduced

def yannakakis_line_join(relations):
    """
    Evaluates a line join query using simplified Yannakakis algorithm.
    Input: list of relations [R1, R2, ..., Rk] where each R_i has 2 attributes
           and joins as R1(A1,A2) ⨝ R2(A2,A3) ⨝ ... ⨝ Rk(Ak,Ak+1)
    Returns: list of result tuples after the join
    """
    # Create a copy to avoid modifying the original
    relations = [r[:] for r in relations]
    
    # ==========================================
    # Phase 1: Backward Sweep (Leaves to Root)
    # ==========================================
    # Iterate from end to start. Filter R_i based on R_{i+1}
    # Logic: If R_i has no match in R_{i+1}, it cannot be part of the result.
    for i in range(len(relations) - 2, -1, -1):
        # R[i] joins R[i+1]. 
        # R[i] join key is index 1. R[i+1] join key is index 0.
        relations[i] = apply_semijoin(relations[i], relations[i+1], 1, 0)

    # ==========================================
    # Phase 2: Forward Sweep (Root to Leaves)
    # ==========================================
    # Iterate from start to end. Filter R_{i+1} based on R_i
    # Logic: If R_{i+1} has no match in R_i, it cannot be part of the result.
    for i in range(0, len(relations) - 1):
        relations[i+1] = apply_semijoin(relations[i+1], relations[i], 0, 1)

    # ==========================================
    # Phase 3: The Join
    # ==========================================
    # Now simply join the reduced relations sequentially.
    # Since they are fully reduced, every join produces valid results (no waste).
    
    final_result = relations[0]
    
    for i in range(1, len(relations)):
        next_rel = relations[i]
        temp_res = []
        
        # Build hash map for next_rel
        idx_map = {}
        for row in next_rel:
            key = row[0] # Join key is always first column for the right table in a chain
            if key not in idx_map: idx_map[key] = []
            idx_map[key].append(row)
            
        # Probe with current results
        for row in final_result:
            key = row[-1] # Join key is always last column of current result
            if key in idx_map:
                for match in idx_map[key]:
                    # Merge: row + match without the join key duplicated
                    new_tuple = row + match[1:]
                    temp_res.append(new_tuple)
        
        final_result = temp_res
    
    return final_result

def problem_2_simplified_yannakakis():
    # ==========================================
    # 1. Dataset Creation (Example 3-line join)
    # q(A1,A2,A3,A4) :- R1(A1,A2), R2(A2,A3), R3(A3,A4)
    # ==========================================
    
    # R1: (A1, A2) - Tuples (1,100) and (2,100) are valid. (9,999) is dead.
    R1 = [(1, 100), (2, 100), (9, 999)]
    
    # R2: (A2, A3) - (100, 20) matches R1 and R3. (888, 55) matches R3 but not R1.
    R2 = [(100, 20), (100, 21), (888, 55)]
    
    # R3: (A3, A4) - (20, 5) matches R2. (55, 7) matches R2's dead tuple.
    R3 = [(20, 5), (21, 6), (55, 7), (99, 99)]

    # The line: R1 --(joins on col 1/0)-- R2 --(joins on col 1/0)-- R3
    relations = [R1, R2, R3]
    
    print("--- Initial Sizes ---")
    print(f"R1: {len(relations[0])}, R2: {len(relations[1])}, R3: {len(relations[2])}")

    # Use the reusable function
    final_result = yannakakis_line_join(relations)
        
    print("\n--- After Reductions (Dangling Tuples Removed) ---")
    print(f"Final result size: {len(final_result)}")

    print("\n--- Final Results ---")
    for row in final_result:
        print(row)

if __name__ == "__main__":
    problem_2_simplified_yannakakis()