from pathlib import Path
import subprocess
from typing import Union


StrListStr = Union[str, list[str], None]
PathStr = Union[str, Path, None]

EXAMPLES_FOLDER = "examples"
RESULTS_FOLDER = "results"
ARGS_FILENAME_SUFFIX = "args"
SPLIT = "__"

def validate_args(args: StrListStr) -> list[str]:
    """convert args to list of strings"""
    if isinstance(args, str):
        args = [args]
    elif args is None:
        args = []
    return args


def run_script(filename: str, args: StrListStr = None) -> tuple[str, str]:
    """run script"""
    args = validate_args(args)
    res = subprocess.run(
        ["python", filename, *args],
        capture_output=True,
        check=False,
    )

    return res.stdout.decode("utf-8"), res.stderr.decode("utf-8")


def get_args(
        filename: Path,
        examples_folder: PathStr = EXAMPLES_FOLDER,
        results_folder: PathStr = RESULTS_FOLDER,
) -> dict[str, str]:
    """get script args from file"""
    args_filename = Path(
        examples_folder,
        results_folder,
        f"{filename.stem}{SPLIT}{ARGS_FILENAME_SUFFIX}.txt"
    )
    with open(args_filename, "r", encoding="utf-8") as file:
        lines = [
            line.split(": ", maxsplit=1)
            for line in file.readlines()
            if not line.startswith("#")
        ]
    return {item[0]: item[1].split() for item in lines}


def read_result(filename: Path, arg_name: str) -> tuple[str, str]:
    """read result from file, return stdout and stderr"""
    result_filename = Path(
        EXAMPLES_FOLDER,
        RESULTS_FOLDER,
        f"{filename.stem}{SPLIT}{arg_name}.txt",
    )
    with open(result_filename, "r", encoding="utf-8") as file:
        text = file.read()
    res, err = text.split("# stdout\n")[1].split("# stderr\n")
    return res, err
