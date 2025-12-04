import random
import time
import problem2  # Import Yannakakis algorithm
import problem3  # Import naive line join

def problem_4_solution():
    # ==========================================
    # 1. Dataset Generation (Random 3-line join)
    # ==========================================
    random.seed(42)  # Fixed seed for reproducibility

    # R1: 100 tuples (i, x) where i = 1..100, x in [1, 5000]
    # Schema: (A, B)
    R1 = [(i, random.randint(1, 5000)) for i in range(1, 101)]

    # R2: 100 tuples (y, j) where j = 1..100, y in [1, 5000]
    # Schema: (B, C). 
    # Note: In the chain R1(A,B)-R2(B,C), R2's first column (y) joins with R1's last column (x).
    R2 = [(random.randint(1, 5000), j) for j in range(1, 101)]

    # R3: 100 tuples (l, l) where l = 1..100
    # Schema: (C, D).
    # Note: In the chain R2(B,C)-R3(C,D), R3's first column matches R2's last column (j).
    R3 = [(l, l) for l in range(1, 101)]

    # The dataset to test
    test_relations = [R1, R2, R3]
    
    print(f"--- Problem 4 Random Dataset Created ---")
    print(f"R1 Size: {len(R1)}, R2 Size: {len(R2)}, R3 Size: {len(R3)}")

    # ==========================================
    # 2. Run Problem 2 Logic (Efficient / Yannakakis)
    # ==========================================
    print("\nRunning Problem 2 Implementation (Yannakakis)...")
    start_time_p2 = time.time()
    
    # Create a copy so we don't modify the original list for Problem 3
    y_relations = [r[:] for r in test_relations]
    p2_result = problem2.yannakakis_line_join(y_relations)

    end_time_p2 = time.time()
    time_p2 = end_time_p2 - start_time_p2

    # ==========================================
    # 3. Run Problem 3 Logic (Naive / Pairwise)
    # ==========================================
    print("Running Problem 3 Implementation (Naive)...")
    start_time_p3 = time.time()

    # Use the naive line join function from Problem 3
    p3_result = problem3.naive_line_join(test_relations)
        
    end_time_p3 = time.time()
    time_p3 = end_time_p3 - start_time_p3

    # ==========================================
    # 4. Compare Results
    # ==========================================
    print("-" * 40)
    print(f"Problem 2 (Efficient) Time : {time_p2:.6f} seconds")
    print(f"Problem 2 Result Count     : {len(p2_result)}")
    print("-" * 40)
    print(f"Problem 3 (Naive) Time     : {time_p3:.6f} seconds")
    print(f"Problem 3 Result Count     : {len(p3_result)}")
    print("-" * 40)

    # Verify identical results (convert to set to ignore order)
    is_same = (set(p2_result) == set(p3_result))
    print(f"Do they return the same results? {is_same}")
    
    if len(p2_result) > 0:
        print(f"Sample Result: {p2_result[0]}")

if __name__ == "__main__":
    problem_4_solution()