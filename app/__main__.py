from .main import Main
from .filedb import FileDB

def main():
    try:
        filedb = FileDB('app/crosswords.txt')
        cli = Main(filedb)
        cli.run_user_interface()
    except FileNotFoundError as err:
        print(str(err))

if __name__ == '__main__':
    main()