from pathlib import Path
import subprocess
from typing import Union


StrListStr = Union[str, list[str], None]
PathStr = Union[str, Path, None]

EXAMPLES_FOLDER = "examples"
RESULTS_FOLDER = "results"
ARGS_FILENAME_SUFFIX = "args"
SPLIT = "__"

DEF_ARGS = {
    "help": "--help",
    "short_flag_help": "-h",
    "no_args": "",
}


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
    name: str,
    examples_folder: PathStr = EXAMPLES_FOLDER,
    results_folder: PathStr = RESULTS_FOLDER,
) -> dict[str, str]:
    """get script args from file"""
    args_filename = Path(
        examples_folder,
        results_folder,
        f"{name}{SPLIT}{ARGS_FILENAME_SUFFIX}.txt",
    )
    with open(args_filename, "r", encoding="utf-8") as file:
        lines = [
            line.split(": ", maxsplit=1)
            for line in file.readlines()
            if line != "\n" and not line.startswith("#")
        ]
    return {item[0]: item[1].split() for item in lines}


def test_args(args: dict[str, str]) -> dict[str, str]:
    """test script args - join defaults with given args"""
    return {**DEF_ARGS, **args}


def write_result(
    name: str,
    stdout: str,
    stderr: str,
    arg_name: str,
    args: list[str] | None,
) -> None:
    """write result to file"""
    if args is None:
        args = []
    result_filename = Path(
        EXAMPLES_FOLDER,
        RESULTS_FOLDER,
        f"{name}{SPLIT}{arg_name}.txt",
    )
    if not result_filename.parent.exists():
        result_filename.parent.mkdir(parents=True)
    with open(result_filename, "w", encoding="utf-8") as file:
        file.write(f"# result for run {name} with args: {', '.join(args)}\n")
        file.write(f"# stdout\n{stdout}# stderr\n{stderr}")


def read_result(name: Path, arg_name: str) -> tuple[str, str]:
    """read result from file, return stdout and stderr.
    If not found, return empty strings
    """
    result_filename = Path(
        EXAMPLES_FOLDER,
        RESULTS_FOLDER,
        f"{name}{SPLIT}{arg_name}.txt",
    )
    if not result_filename.exists():
        return "", ""
    with open(result_filename, "r", encoding="utf-8") as file:
        text = file.read()
    res, err = text.split("# stdout\n")[1].split("# stderr\n")
    return res, err
