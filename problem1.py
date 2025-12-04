def problem_1_hash_join(R1, R2):
    print("--- R1 Tuples (A, B) ---")
    for t in R1: print(t)
    print("\n--- R2 Tuples (B, C) ---")
    for t in R2: print(t)

    # ==========================================
    # Implement Algorithm (Hash Join)
    # ==========================================
    results = []
    
    # STEP 1: Build Phase - Hash tuples of R2
    # h[b] = { t in R2 | pi_B(t) = b }
    h = {}
    
    for t in R2:
        # t is (B, C), so pi_B(t) is t[0]
        join_key_b = t[0]
        
        # Standard dictionary logic to handle lists
        if join_key_b not in h:
            h[join_key_b] = []
        h[join_key_b].append(t)

    # STEP 2: Probe Phase - Iterate over t' in R1
    # [cite_start]Iterate over each tuple t' in R1 [cite: 960]
    for t_prime in R1:
        # t_prime is (A, B), so pi_B(t') is t_prime[1]
        probe_key = t_prime[1]
        
        # [cite_start]Probe the hash map with pi_B(t') [cite: 960]
        if probe_key in h:
            # [cite_start]Report all tuples in R2 that can be joined [cite: 960]
            matching_tuples_in_R2 = h[probe_key]
            
            for t_match in matching_tuples_in_R2:
                # Result tuple: (A, B, C)
                # t_prime[0] is A, t_prime[1] is B (which equals t_match[0]), t_match[1] is C
                join_tuple = (t_prime[0], t_prime[1], t_match[1])
                results.append(join_tuple)

    # ==========================================
    # 3. Report Results
    # ==========================================
    print("\n--- Join Results q(A,B,C) ---")
    print(f"Total Results: {len(results)}")
    for res in results:
        print(res)

def hash_join(relation_left, relation_right):
    """
    Implements R_left ⨝ R_right using a Hash Join.
    - Hashes the Right Relation on its FIRST column (Attribute B).
    - Probes with the Left Relation on its LAST column (Attribute B).
    """
    results = []
    
    # 1. Build Phase: Hash relation_right
    # h[key] = list of matching tuples
    h = {}
    for r in relation_right:
        key = r[0] # Join key is the first column of the right relation
        if key not in h:
            h[key] = []
        h[key].append(r)
        
    # 2. Probe Phase: Scan relation_left
    for l in relation_left:
        key = l[-1] # Join key is the last column of the left relation
        
        if key in h:
            # Join logic: Combine left tuple + right tuple (excluding duplicate key)
            matching_tuples = h[key]
            for m in matching_tuples:
                # m[1:] slices off the join key from the right tuple to avoid duplication
                new_tuple = l + m[1:]
                results.append(new_tuple)
                
    return results

# ==========================================
# Dataset for Problem 1
# ==========================================
R1 = [
    (1, 100), (2, 100), (3, 200), (4, 200), (5, 300),
    (6, 400), (7, 500), (8, 600), (9, 700), (10, 800)
]

# R2 has schema (B, C)
# 100, 200, 300, 400 exist in R1. 900, 999 do not.
# Fixed: Exactly 10 tuples as required (removed one duplicate tuple)
R2 = [
    (100, 10), (100, 11),  # B=100
    (200, 20),             # B=200
    (300, 30),             # B=300
    (400, 40), (400, 41),  # B=400
    (900, 90),             # B=900 (No match)
    (999, 99), (999, 98),  # B=999 (No match)
    (500, 55)              # B=500
]

if __name__ == "__main__":
    # Run the function
    problem_1_hash_join(R1, R2)
    print("\n" + "="*50)
    x = hash_join(R1, R2)
    print("Result of hash join:", x)