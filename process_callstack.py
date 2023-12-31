import argparse
import re
import subprocess

def get_symbol_table(executable_file):
    try:
        result = subprocess.check_output(['nm', '-C', executable_file])
        symbol_table = {}
        for line in result.decode('utf-8').splitlines():
            parts = line.split()
            if len(parts) >= 3:
                address, symbol_type, *symbol_name = parts
                symbol_table[int(address, 16)] = ' '.join(symbol_name)
        return symbol_table
    except subprocess.CalledProcessError:
        print(f"Unable to get symbol table for {executable_file}")
        return {}

def process_pc_trace(executable_files, pc_trace_file, output_file):
    # Get all symbol tables
    all_symbol_tables = {}
    for file in executable_files:
        symbol_table = get_symbol_table(file)
        all_symbol_tables[file] = symbol_table

    # Read the PC trace file and index the symbol tables
    output_list = []
    with open(pc_trace_file, 'r') as trace_file:
        for line in trace_file:
            match = re.search(r'Cycle\s+(\d+).*Pc\[(\w+)\]', line)
            if match:
                cycle = match.group(1)
                pc = match.group(2)

                # Modify the PC address if it starts with 0xffffffc00
                pc_address = int(pc, 16)
                if pc_address & 0xfffffffff0000000 == 0xffffffc000000000:
                    pc_address = (pc_address & 0xffffffff) | 0x80000000

                for file, symbol_table in all_symbol_tables.items():
                    if pc_address in symbol_table:
                        symbol = symbol_table[pc_address]
                        output_list.append((cycle, pc, file, symbol))
                        break

    # Save the output list to a file
    with open(output_file, 'w') as output:
        for item in output_list:
            cycle, pc, file, symbol = item
            output.write(f"Cycle: {cycle}, PC: {pc}, File: {file}, Symbol: {symbol}\n")


def main():
    parser = argparse.ArgumentParser(description='Get symbol table from executable files')
    parser.add_argument('executable_files', nargs='+', help='List of executable files to get symbol table from')
    parser.add_argument('-t', '--trace-file', dest='pc_trace_file', help='File containing PC value trace of an executable file')
    parser.add_argument('-o', '--output-file', dest='output_file', help='Output file')
    args = parser.parse_args()

    process_pc_trace(args.executable_files, args.pc_trace_file, args.output_file)

if __name__ == '__main__':
    main()
