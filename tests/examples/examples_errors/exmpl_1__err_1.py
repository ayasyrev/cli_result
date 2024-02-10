# diff output from exmpl_1.txt
# different help
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--e",
)


if __name__ == "__main__":
    args = parser.parse_args()
    print(args.echo)
