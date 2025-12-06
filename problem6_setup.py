import csv
import random
import os

def generate_problem6_data():
    print("Generating datasets for Problem 6...")
    random.seed(42)

    # Logic from problem5.py
    
    # --- R1 (A, B) ---
    # 1000 tuples (i, 5), 1000 tuples (i, 7), 1 tuple (2001, 2002)
    r1_part1 = [(i, 5) for i in range(1, 1001)]
    r1_part2 = [(i, 7) for i in range(1001, 2001)]
    r1_part3 = [(2001, 2002)]
    R1 = r1_part1 + r1_part2 + r1_part3
    random.shuffle(R1)

    # --- R2 (B, C) ---
    # 1000 tuples (5, i), 1000 tuples (7, i), 1 tuple (2002, 8)
    r2_part1 = [(5, i) for i in range(1, 1001)]
    r2_part2 = [(7, i) for i in range(1001, 2001)]
    r2_part3 = [(2002, 8)]
    R2 = r2_part1 + r2_part2 + r2_part3
    random.shuffle(R2)

    # --- R3 (C, D) ---
    # 2000 tuples (x, y) with x >= 2002 (no overlap with 5/7), 1 tuple (8, 30)
    R3 = [(random.randint(2002, 3000), random.randint(1, 3000)) for _ in range(2000)]
    R3.append((8, 30))
    random.shuffle(R3)

    # Export to CSV
    def write_csv(filename, data, headers):
        # Use absolute path to ensure you find the files easily
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"Created {filename} with {len(data)} rows.")

    write_csv('R1.csv', R1, ['A', 'B'])
    write_csv('R2.csv', R2, ['B', 'C'])
    write_csv('R3.csv', R3, ['C', 'D'])

if __name__ == "__main__":
    generate_problem6_data()