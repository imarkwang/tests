import argparse
import subprocess

def get_symbol_table(executable_file):
    try:
        result = subprocess.check_output(['nm', '-C', executable_file])
        return result.decode('utf-8')
    except subprocess.CalledProcessError:
        print(f"无法获取 {executable_file} 的符号表")
        return ''

def main():
    parser = argparse.ArgumentParser(description='获取可执行文件的符号表')
    parser.add_argument('executable_files', nargs='+', help='要获取符号表的可执行文件列表')
    args = parser.parse_args()

    for file in args.executable_files:
        symbol_table = get_symbol_table(file)
        print(f"文件: {file}")
        print(symbol_table)
        print('-' * 50)

if __name__ == '__main__':
    main()
