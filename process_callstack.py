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
                symbol_table[int(address, 16)] = {
                    'name': ' '.join(symbol_name),
                    'type': symbol_type
                }
        return symbol_table
    except subprocess.CalledProcessError:
        print(f"Unable to get symbol table for {executable_file}")
        return {}

def build_call_stack(address, symbol_table, call_stack):
    if address in symbol_table:
        symbol = symbol_table[address]
        call_stack.append(symbol)
        if symbol['type'] == 'T':  # Function symbol
            target_address = int(symbol['name'].split()[-1], 16)
            build_call_stack(target_address, symbol_table, call_stack)

def process_pc_trace(executable_files, pc_trace_file, output_file):
    # Get all symbol tables
    all_symbol_tables = {}
    for file in executable_files:
        symbol_table = get_symbol_table(file)
        all_symbol_tables[file] = symbol_table

    # Read the PC trace file and build call stacks
    call_stacks = []
    with open(pc_trace_file, 'r') as trace_file:
        for line in trace_file:
            match = re.search(r'Pc\[(\w+)\]', line)
            if match:
                pc = match.group(1)
                pc_address = int(pc, 16)
                for file, symbol_table in all_symbol_tables.items():
                    if pc_address in symbol_table:
                        call_stack = []
                        build_call_stack(pc_address, symbol_table, call_stack)
                        call_stacks.append((file, call_stack))
                        break

    # Save the call stacks to the output file
    with open(output_file, 'w') as output:
        for file, call_stack in call_stacks:
            output.write(f"File: {file}\n")
            for symbol in call_stack:
                output.write(f"- {symbol['name']}\n")
            output.write("\n")

def main():
    parser = argparse.ArgumentParser(description='Get symbol table from executable files')
    parser.add_argument('executable_files', nargs='+', help='List of executable files to get symbol table from')
    parser.add_argument('-t', '--trace-file', dest='pc_trace_file', help='File containing PC value trace of an executable file')
    parser.add_argument('-o', '--output-file', dest='output_file', help='Output file')
    args = parser.parse_args()

    process_pc_trace(args.executable_files, args.pc_trace_file, args.output_file)

if __name__ == '__main__':
    main()
