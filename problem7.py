import pandas as pd
import time
import collections
import numpy as np

# ==========================================
# QUERY DEFINITION
# ==========================================
# Query: q(A1, A2, A3, A4, A5, A6) :- 
#        R1(A1, A2), R2(A2, A3), R3(A1, A3), 
#        R4(A3, A4), R5(A4, A5), R6(A5, A6), R7(A4, A6)
#
# Query structure:
#   - Triangle 1: R1, R2, R3 (variables A1, A2, A3)
#   - Edge: R4 (variables A3, A4)
#   - Triangle 2: R5, R6, R7 (variables A4, A5, A6)


# ==========================================
# DATA LOADING AND UTILITIES
# ==========================================

def _convert_to_python_type(value):
    """Convert numpy types to Python native types."""
    if isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    return value


def load_relations():
    """Load all relations from CSV files into memory."""
    relations = {}
    for i in range(1, 8):
        df = pd.read_csv(f'query_relations/R{i}.csv')
        # Convert numpy types to Python native types (np.int64 -> int)
        relations[f'R{i}'] = [
            tuple(_convert_to_python_type(x) for x in row)
            for row in df.values
        ]
    return relations


def build_index(relation, column_index):
    """
    Build an index on a specific column of a relation.
    Returns: Dictionary mapping column value -> list of tuples with that value.
    """
    index = collections.defaultdict(list)
    for tuple_row in relation:
        key_value = tuple_row[column_index]
        index[key_value].append(tuple_row)
    return index


# ==========================================
# SCHEMA DEFINITION
# ==========================================
# Define which variables appear in which relations and at what column positions

RELATION_SCHEMA = {
    'R1': ('A1', 'A2'),  # R1[0]=A1, R1[1]=A2
    'R2': ('A2', 'A3'),  # R2[0]=A2, R2[1]=A3
    'R3': ('A1', 'A3'),  # R3[0]=A1, R3[1]=A3
    'R4': ('A3', 'A4'),  # R4[0]=A3, R4[1]=A4
    'R5': ('A4', 'A5'),  # R5[0]=A4, R5[1]=A5
    'R6': ('A5', 'A6'),  # R6[0]=A5, R6[1]=A6
    'R7': ('A4', 'A6'),  # R7[0]=A4, R7[1]=A6
}


def get_variable_locations(variable):
    """
    Get all (relation_name, column_index) pairs where this variable appears.
    Example: get_variable_locations('A1') returns [('R1', 0), ('R3', 0)]
    """
    locations = []
    for relation_name, (var1, var2) in RELATION_SCHEMA.items():
        if variable == var1:
            locations.append((relation_name, 0))
        elif variable == var2:
            locations.append((relation_name, 1))
    return locations


# ==========================================
# ALGORITHM 1: GENERIC JOIN
# ==========================================
# Generic Join algorithm uses recursive intersection:
#   1. For each variable in order, find all possible values by intersecting
#      projections from all relations containing that variable
#   2. For each valid value, filter relations and recurse

def generic_join_recursive(partial_tuple, remaining_variables, filtered_relations):
    """
    Recursively build the join result tuple by tuple.
    
    Args:
        partial_tuple: Tuple of values assigned so far (e.g., (a1, a2))
        remaining_variables: List of variables still to assign (e.g., ['A3', 'A4', ...])
        filtered_relations: Dict of relation_name -> list of tuples that match partial_tuple
    
    Returns:
        List of complete tuples (A1, A2, A3, A4, A5, A6)
    """
    # Base case: all variables assigned, return the complete tuple
    if not remaining_variables:
        return [partial_tuple]
    
    # Get the next variable to process
    current_variable = remaining_variables[0]
    next_variables = remaining_variables[1:]
    
    # Find all relations that contain this variable
    variable_locations = get_variable_locations(current_variable)
    
    # Step 1: Compute intersection of all possible values for this variable
    # We project the variable from each relation and intersect the sets
    possible_values = None
    
    for relation_name, column_index in variable_locations:
        if relation_name not in filtered_relations:
            continue
            
        # Project this variable from the filtered relation
        values_in_relation = {row[column_index] for row in filtered_relations[relation_name]}
        
        if possible_values is None:
            possible_values = values_in_relation
        else:
            possible_values = possible_values & values_in_relation  # Intersection
        
        # Early termination: if intersection is empty, no valid tuples exist
        if not possible_values:
            return []
    
    # Step 2: For each valid value, recurse
    results = []
    
    for value in possible_values:
        # Filter relations to only include tuples matching this value
        new_filtered_relations = {}
        
        for relation_name, relation_tuples in filtered_relations.items():
            # Check if this relation contains the current variable
            contains_variable = any(
                rel_name == relation_name 
                for rel_name, _ in variable_locations
            )
            
            if contains_variable:
                # Filter: keep only tuples where variable matches the value
                column_index = next(
                    col_idx 
                    for rel_name, col_idx in variable_locations 
                    if rel_name == relation_name
                )
                new_tuples = [
                    row for row in relation_tuples 
                    if row[column_index] == value
                ]
                new_filtered_relations[relation_name] = new_tuples
            else:
                # Relation doesn't contain this variable, keep all tuples
                new_filtered_relations[relation_name] = relation_tuples
        
        # Recurse with extended tuple and filtered relations
        extended_tuple = partial_tuple + (value,)
        sub_results = generic_join_recursive(
            extended_tuple, 
            next_variables, 
            new_filtered_relations
        )
        results.extend(sub_results)
    
    return results


def run_generic_join(all_relations):
    """
    Run Generic Join algorithm on the query.
    
    Algorithm:
        - Process variables in order: A1, A2, A3, A4, A5, A6
        - For each variable, intersect projections from all containing relations
        - Recursively build complete tuples
    
    Time Complexity: O(N^w) where w is the fractional hypertree width
    """
    variables = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']
    return generic_join_recursive((), variables, all_relations.copy())


# ==========================================
# ALGORITHM 2: GENERALIZED HYPERTREE WIDTH (GHW)
# ==========================================
# GHW uses tree decomposition:
#   - Decompose query into bags (subproblems)
#   - Solve each bag using standard joins
#   - Join the bags together

def join_two_relations(left_relation, right_relation, left_join_col, right_join_col):
    """
    Join two relations on specified columns using hash join.
    
    Returns: List of joined tuples
    """
    # Build index on right relation
    right_index = build_index(right_relation, right_join_col)
    
    results = []
    for left_tuple in left_relation:
        join_key = left_tuple[left_join_col]
        if join_key in right_index:
            for right_tuple in right_index[join_key]:
                # Combine tuples, avoiding duplicate join key
                joined = left_tuple + (right_tuple[1 - right_join_col],)
                results.append(joined)
    
    return results


def compute_bag1_triangle_naive(r1, r2, r3):
    """
    Compute Bag 1: Triangle {A1, A2, A3} from R1, R2, R3.
    Uses standard hash joins (naive approach).
    
    Steps:
        1. Join R1(A1, A2) with R2(A2, A3) on A2 -> temp(A1, A2, A3)
        2. Join temp with R3(A1, A3) on (A1, A3) -> bag1(A1, A2, A3)
    """
    # Step 1: R1 ⨝ R2 on A2
    # R1[1] = A2, R2[0] = A2
    temp = join_two_relations(r1, r2, left_join_col=1, right_join_col=0)
    
    # Step 2: Filter temp by R3
    # temp has (A1, A2, A3), R3 has (A1, A3)
    # We need temp[0]=A1, temp[2]=A3 to match R3
    r3_set = set(r3)
    bag1 = [
        (a1, a2, a3) for a1, a2, a3 in temp 
        if (a1, a3) in r3_set
    ]
    
    return bag1


def compute_bag3_triangle_naive(r5, r6, r7):
    """
    Compute Bag 3: Triangle {A4, A5, A6} from R5, R6, R7.
    Uses standard hash joins (naive approach).
    
    Steps:
        1. Join R5(A4, A5) with R6(A5, A6) on A5 -> temp(A4, A5, A6)
        2. Join temp with R7(A4, A6) on (A4, A6) -> bag3(A4, A5, A6)
    """
    # Step 1: R5 ⨝ R6 on A5
    # R5[1] = A5, R6[0] = A5
    temp = join_two_relations(r5, r6, left_join_col=1, right_join_col=0)
    
    # Step 2: Filter temp by R7
    # temp has (A4, A5, A6), R7 has (A4, A6)
    # We need temp[0]=A4, temp[2]=A6 to match R7
    r7_set = set(r7)
    bag3 = [
        (a4, a5, a6) for a4, a5, a6 in temp 
        if (a4, a6) in r7_set
    ]
    
    return bag3


def run_ghw(all_relations):
    """
    Run Generalized Hypertree Width (GHW) algorithm.
    
    Tree Decomposition:
        - Bag 1: Triangle {A1, A2, A3} from R1, R2, R3
        - Bag 2: Edge {A3, A4} from R4
        - Bag 3: Triangle {A4, A5, A6} from R5, R6, R7
    
    Algorithm:
        1. Compute each bag using standard joins
        2. Join bags in tree order: Bag1 ⨝ Bag2 ⨝ Bag3
    
    Time Complexity: O(N^2) for each triangle bag, then O(N) for acyclic joins
    """
    # Step 1: Compute each bag
    bag1 = compute_bag1_triangle_naive(
        all_relations['R1'],
        all_relations['R2'],
        all_relations['R3']
    )
    
    bag2 = all_relations['R4']  # Bag 2 is just R4
    
    bag3 = compute_bag3_triangle_naive(
        all_relations['R5'],
        all_relations['R6'],
        all_relations['R7']
    )
    
    # Step 2: Join bags in tree order
    # Join Bag1(A1, A2, A3) with Bag2(A3, A4) on A3
    # bag1[2] = A3, bag2[0] = A3
    bag2_index = build_index(bag2, column_index=0)
    partial_result = []
    for bag1_tuple in bag1:
        a3_value = bag1_tuple[2]
        if a3_value in bag2_index:
            for bag2_tuple in bag2_index[a3_value]:
                # bag2_tuple is (A3, A4), we want A4
                a4_value = bag2_tuple[1]
                partial_result.append(bag1_tuple + (a4_value,))
    
    # Join partial result with Bag3(A4, A5, A6) on A4
    # partial_result[3] = A4, bag3[0] = A4
    bag3_index = build_index(bag3, column_index=0)
    final_result = []
    for partial_tuple in partial_result:
        a4_value = partial_tuple[3]
        if a4_value in bag3_index:
            for bag3_tuple in bag3_index[a4_value]:
                # bag3_tuple is (A4, A5, A6), we want A5 and A6
                a5_value = bag3_tuple[1]
                a6_value = bag3_tuple[2]
                final_result.append(partial_tuple + (a5_value, a6_value))
    
    return final_result


# ==========================================
# ALGORITHM 3: FRACTIONAL HYPERTREE WIDTH (FHW)
# ==========================================
# FHW also uses tree decomposition, but computes bags using Generic Join
# instead of naive joins, which is more efficient for dense subproblems

def compute_triangle_with_generic_join(relation_a, relation_b, relation_c):
    """
    Compute triangle join using Generic Join approach (intersections).
    
    Relations form a triangle:
        - relation_a connects var1 and var2
        - relation_b connects var2 and var3
        - relation_c connects var1 and var3
    
    Algorithm:
        1. Intersect var1 values from relation_a and relation_c
        2. For each var1, intersect var2 from relation_a and relation_b
        3. For each (var1, var2), intersect var3 from all three relations
    
    Returns: List of tuples (var1, var2, var3)
    """
    # Build indices for efficient lookup
    index_a_on_var1 = build_index(relation_a, column_index=0)
    index_b_on_var2 = build_index(relation_b, column_index=0)
    index_c_on_var1 = build_index(relation_c, column_index=0)
    
    # Step 1: Intersect var1 values from relation_a and relation_c
    var1_values_a = set(index_a_on_var1.keys())
    var1_values_c = set(index_c_on_var1.keys())
    valid_var1_values = var1_values_a & var1_values_c
    
    results = []
    
    # Step 2: For each valid var1, find valid var2 and var3
    for var1 in valid_var1_values:
        # Get var2 values from relation_a for this var1
        var2_values_from_a = {row[1] for row in index_a_on_var1[var1]}
        
        # Get var3 values from relation_c for this var1
        var3_values_from_c = {row[1] for row in index_c_on_var1[var1]}
        
        # Step 3: For each var2, find valid var3 values
        for var2 in var2_values_from_a:
            if var2 not in index_b_on_var2:
                continue
                
            # Get var3 values from relation_b for this var2
            var3_values_from_b = {row[1] for row in index_b_on_var2[var2]}
            
            # Intersect var3 values from all three sources
            valid_var3_values = var3_values_from_c & var3_values_from_b
            
            # Create results for all valid (var1, var2, var3) combinations
            for var3 in valid_var3_values:
                results.append((var1, var2, var3))
    
    return results


def run_fhw(all_relations):
    """
    Run Fractional Hypertree Width (FHW) algorithm.
    
    Uses the same tree decomposition as GHW:
        - Bag 1: Triangle {A1, A2, A3} from R1, R2, R3
        - Bag 2: Edge {A3, A4} from R4
        - Bag 3: Triangle {A4, A5, A6} from R5, R6, R7
    
    Algorithm:
        1. Compute each bag using Generic Join (intersection-based)
        2. Join bags in tree order (same as GHW)
    
    Time Complexity: O(N^fhw) where fhw is fractional hypertree width
    """
    # Step 1: Compute bags using Generic Join approach
    bag1 = compute_triangle_with_generic_join(
        all_relations['R1'],  # (A1, A2)
        all_relations['R2'],  # (A2, A3)
        all_relations['R3']   # (A1, A3)
    )
    
    bag2 = all_relations['R4']  # Bag 2 is just R4
    
    bag3 = compute_triangle_with_generic_join(
        all_relations['R5'],  # (A4, A5)
        all_relations['R6'],  # (A5, A6)
        all_relations['R7']   # (A4, A6)
    )
    
    # Step 2: Join bags (same as GHW)
    # Join Bag1 with Bag2 on A3
    bag2_index = build_index(bag2, column_index=0)
    partial_result = []
    for bag1_tuple in bag1:
        a3_value = bag1_tuple[2]
        if a3_value in bag2_index:
            for bag2_tuple in bag2_index[a3_value]:
                a4_value = bag2_tuple[1]
                partial_result.append(bag1_tuple + (a4_value,))
    
    # Join partial result with Bag3 on A4
    bag3_index = build_index(bag3, column_index=0)
    final_result = []
    for partial_tuple in partial_result:
        a4_value = partial_tuple[3]
        if a4_value in bag3_index:
            for bag3_tuple in bag3_index[a4_value]:
                a5_value = bag3_tuple[1]
                a6_value = bag3_tuple[2]
                final_result.append(partial_tuple + (a5_value, a6_value))
    
    return final_result


# ==========================================
# MAIN EXECUTION
# ==========================================

def problem_7_solution():
    """Run all three algorithms and compare their performance."""
    print("=" * 60)
    print("Problem 7: Query Evaluation Algorithms")
    print("=" * 60)
    print(f"\nQuery: q(A1, A2, A3, A4, A5, A6) :-")
    print(f"  R1(A1, A2), R2(A2, A3), R3(A1, A3),")
    print(f"  R4(A3, A4), R5(A4, A5), R6(A5, A6), R7(A4, A6)\n")
    
    # Load data
    print("Loading relations from CSV files...")
    all_relations = load_relations()
    for rel_name in sorted(all_relations.keys()):
        print(f"  {rel_name}: {len(all_relations[rel_name])} tuples")
    print()
    
    # Run Generic Join
    print("-" * 60)
    print("Algorithm 1: Generic Join")
    print("-" * 60)
    start_time = time.time()
    result_generic = run_generic_join(all_relations)
    time_generic = time.time() - start_time
    print(f"Result count: {len(result_generic)}")
    print(f"Time: {time_generic:.6f} seconds")
    if result_generic:
        print(f"Sample result: {result_generic[0]}")
    print()
    
    # Run GHW
    print("-" * 60)
    print("Algorithm 2: Generalized Hypertree Width (GHW)")
    print("-" * 60)
    start_time = time.time()
    result_ghw = run_ghw(all_relations)
    time_ghw = time.time() - start_time
    print(f"Result count: {len(result_ghw)}")
    print(f"Time: {time_ghw:.6f} seconds")
    if result_ghw:
        print(f"Sample result: {result_ghw[0]}")
    print()
    
    # Run FHW
    print("-" * 60)
    print("Algorithm 3: Fractional Hypertree Width (FHW)")
    print("-" * 60)
    start_time = time.time()
    result_fhw = run_fhw(all_relations)
    time_fhw = time.time() - start_time
    print(f"Result count: {len(result_fhw)}")
    print(f"Time: {time_fhw:.6f} seconds")
    if result_fhw:
        print(f"Sample result: {result_fhw[0]}")
    print()
    
    # Verify all algorithms return same results
    print("-" * 60)
    print("Verification: Comparing Results")
    print("-" * 60)
    set_generic = set(result_generic)
    set_ghw = set(result_ghw)
    set_fhw = set(result_fhw)
    
    all_match = (set_generic == set_ghw == set_fhw)
    print(f"All algorithms return same results: {all_match}")
    if not all_match:
        print(f"  Generic Join: {len(set_generic)} unique tuples")
        print(f"  GHW:          {len(set_ghw)} unique tuples")
        print(f"  FHW:          {len(set_fhw)} unique tuples")
    
    # Summary
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    print(f"{'Algorithm':<30} {'Time (s)':<15} {'Results':<10}")
    print("-" * 60)
    print(f"{'Generic Join':<30} {time_generic:<15.6f} {len(result_generic):<10}")
    print(f"{'GHW':<30} {time_ghw:<15.6f} {len(result_ghw):<10}")
    print(f"{'FHW':<30} {time_fhw:<15.6f} {len(result_fhw):<10}")
    print("=" * 60)


if __name__ == "__main__":
    problem_7_solution()