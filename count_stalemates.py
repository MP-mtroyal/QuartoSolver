def save_solutions_ending_in_one(input_file, output_file):
    count, lines = 0, 0
    with open(input_file, 'r') as fin: #, open(output_file, 'w') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                hash_val, solution = line.split(',', 1)
                if solution:
                    lines += 1
                if solution.endswith('1'):
                    #fout.write(f"{hash_val},{solution}\n")
                    count += 1
            except ValueError:
                continue  # skip malformed lines
    #print (f"Saved {count} solutions ending in '1' to '{output_file}'.")
    print(lines)
    print(count)
    return count

input_path = "./Solved_Unsolved/Agl_Level_8_solved.txt"
output_path = "./Solved_Unsolved/stalemates.txt"
save_solutions_ending_in_one(input_path, output_path)

