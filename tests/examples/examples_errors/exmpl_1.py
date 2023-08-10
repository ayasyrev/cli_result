import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "--echo",
)


if __name__ == "__main__":
    args = parser.parse_args()
    print(args.echo)
