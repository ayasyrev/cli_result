# alternative version for example_extra_1.py, expecting same results
# same, but different parser name - just for example
# used __ as split at file name
import argparse


parser_different_name = argparse.ArgumentParser()
parser_different_name.add_argument(
    "--echo",
)


if __name__ == "__main__":
    args = parser_different_name.parse_args()
    print(args.echo)
