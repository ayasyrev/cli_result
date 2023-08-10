# diff output from exmpl_1.txt
# diff in result - extra output
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "--echo",
)


if __name__ == "__main__":
    args = parser.parse_args()
    print(args.echo)
    print("this is diff for ERR!")
