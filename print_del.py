import argparse
import re

def delete_lines_between_pcs(file_path, start_pc, end_pc):
    start_pc_found = False
    start_pc_count = 0

    # 读取文件并删除指定范围内的行
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        pc = extract_pc_from_line(line)

        if pc == start_pc:
            if start_pc_found:
                raise ValueError('Multiple start PCs detected.')
            start_pc_found = True
            start_pc_count += 1
            continue

        if pc == end_pc:
            if not start_pc_found:
                raise ValueError('No start PC detected before end PC.')
            start_pc_found = False
            continue

        if not start_pc_found:
            new_lines.append(line)

    if start_pc_found:
        raise ValueError('No end PC detected after start PC.')

    # 写入修改后的内容到文件
    with open(file_path, 'w') as file:
        file.writelines(new_lines)

def extract_pc_from_line(line):
    pattern = r'\[0x([\da-fA-F]+)\]'
    match = re.search(pattern, line)
    if match:
        return match.group(1)
    else:
        raise ValueError('Invalid line format: ' + line.strip())

def main():
    parser = argparse.ArgumentParser(description='Delete lines between start PC and end PC in a file')
    parser.add_argument('file_path', type=str, help='path to the input file')
    parser.add_argument('start_pc', type=str, help='start PC value')
    parser.add_argument('end_pc', type=str, help='end PC value')

    args = parser.parse_args()

    try:
        delete_lines_between_pcs(args.file_path, args.start_pc, args.end_pc)
        print('Lines between start PC and end PC deleted successfully.')
    except ValueError as e:
        print('Error:', str(e))

if __name__ == '__main__':
    main()
