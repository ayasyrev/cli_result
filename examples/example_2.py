import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "--echo",
)

subparsers = parser.add_subparsers(help="sub-command help")
parser_a = subparsers.add_parser("a", help="a help")
parser_a.add_argument("bar", type=int, help="bar help")

parser_b = subparsers.add_parser("b", help="b help")
parser_b.add_argument("--baz", choices="XYZ", help="baz help")


if __name__ == "__main__":
    args = parser.parse_args()
    if hasattr(args, "bar"):
        print(f"cmd a: bar={args.bar}")
    elif hasattr(args, "baz"):
        print(f"cmd b: baz={args.baz}")
    print(f"main: echo={args.echo}")
