from .command_line_interface import CLI
from .filedb import FileDB

def main():
    try:
        filedb = FileDB('app/crosswords.txt')
        cli = CLI(filedb)
        cli.run()
    except FileNotFoundError as err:
        print(str(err))

if __name__ == '__main__':
    main()