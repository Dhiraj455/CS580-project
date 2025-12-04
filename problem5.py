import random
import time
import problem2  # Import Yannakakis algorithm
import problem3  # Import naive line join

def problem_5_solution():
    # ==========================================
    # 1. Dataset Generation (Adversarial)
    # ==========================================
    # This dataset creates a massive intermediate result in R1 ⨝ R2
    # which is then almost entirely filtered out by R3.
    random.seed(42)

    # --- Construct R1 ---
    # Schema (A, B)
    # 1000 tuples (i, 5)
    r1_part1 = [(i, 5) for i in range(1, 1001)]
    # 1000 tuples (i, 7)
    r1_part2 = [(i, 7) for i in range(1001, 2001)]
    # 1 specific tuple
    r1_part3 = [(2001, 2002)]
    
    R1 = r1_part1 + r1_part2 + r1_part3
    random.shuffle(R1)

    # --- Construct R2 ---
    # Schema (B, C)
    # 1000 tuples (5, i) -> joins with r1_part1 to make 1000*1000 rows
    r2_part1 = [(5, i) for i in range(1, 1001)]
    # 1000 tuples (7, i) -> joins with r1_part2 to make 1000*1000 rows
    r2_part2 = [(7, i) for i in range(1001, 2001)]
    # 1 specific tuple -> joins with r1_part3
    r2_part3 = [(2002, 8)]
    
    R2 = r2_part1 + r2_part2 + r2_part3
    random.shuffle(R2)

    # --- Construct R3 ---
    # Schema (C, D)
    # 2000 random tuples (x, y) where x >= 2002.
    # Crucially, x is NEVER 5 or 7, nor any 'i' from the massive join above.
    # These effectively act as a filter.
    R3 = [(random.randint(2002, 3000), random.randint(1, 3000)) for _ in range(2000)]
    # 1 specific tuple -> joins with the survivor chain
    R3.append((8, 30))
    random.shuffle(R3)

    test_relations = [R1, R2, R3]
    print(f"--- Problem 5 Adversarial Dataset Created ---")
    print(f"R1: {len(R1)}, R2: {len(R2)}, R3: {len(R3)}")

    # ==========================================
    # 2. Run Problem 2 (Efficient Yannakakis)
    # ==========================================
    print("\nRunning Problem 2 (Efficient)...")
    start_time_p2 = time.time()
    
    # Working copy
    y_relations = [r[:] for r in test_relations]
    p2_result = problem2.yannakakis_line_join(y_relations)

    end_time_p2 = time.time()
    time_p2 = end_time_p2 - start_time_p2

    # ==========================================
    # 3. Run Problem 3 (Naive)
    # ==========================================
    print("Running Problem 3 (Naive)...")
    print("Warning: This may take a moment due to intermediate explosion...")
    start_time_p3 = time.time()

    # Use the naive line join function from Problem 3
    p3_result = problem3.naive_line_join(test_relations)
        
    end_time_p3 = time.time()
    time_p3 = end_time_p3 - start_time_p3

    # ==========================================
    # 4. Results & Analysis
    # ==========================================
    print("-" * 40)
    print(f"Problem 2 (Efficient) Time : {time_p2:.6f} seconds")
    print(f"Problem 2 Result Count     : {len(p2_result)}")
    print("-" * 40)
    print(f"Problem 3 (Naive) Time     : {time_p3:.6f} seconds")
    print(f"Problem 3 Result Count     : {len(p3_result)}")
    print("-" * 40)
    
    match = (set(p2_result) == set(p3_result))
    print(f"Results Match: {match}")
    if len(p2_result) > 0:
        print(f"Result Tuple: {p2_result[0]}")
    if len(p3_result) > 0:
        print(f"Result Tuple: {p3_result[0]}")

if __name__ == "__main__":
    problem_5_solution()