"""Test for run scripts and compare output with expected results."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple, Union

StrListStr = Union[str, List[str], None]
PathStr = Union[str, Path, None]


ARGPARSE_OLD = sys.version_info.minor < 10


@dataclass
class Cfg:
    """Base config for cli_result"""

    examples_path: str = "examples"
    results_path: str = "results"
    args_filename_suffix: str = "args"
    split: str = "__"


class Example(NamedTuple):
    """Example - name and list of files"""

    name: str
    files: list[Path]


class Args(NamedTuple):
    """Args - name and list of arguments"""

    name: str
    list: list[str] | None


class Result(NamedTuple):
    """Result - stdout and stderr"""

    stdout: str
    stderr: str
    returncode: int = 0


class Error(NamedTuple):
    """Error - argname / filename / res (result) / exp (expected)"""

    argname: str
    filename: str
    res: str
    exp: str


class ExampleError(NamedTuple):
    """Example Errors - example name / list of Errors"""

    name: str
    list: list[Error]


def get_examples(
    names: str | List[str] | None = None,
    cfg: Cfg | None = None,
) -> List[Example]:
    """get examples names"""
    cfg = Cfg() if cfg is None else cfg
    file_names: Dict[str, List[Path]] = defaultdict(list)
    for filename in Path(cfg.examples_path).glob("*.py"):
        example_name = filename.stem.split(cfg.split)[0]
        if example_name == filename.stem:
            file_names[example_name].insert(0, filename)
        else:
            file_names[example_name].append(filename)
    if names is not None:
        if isinstance(names, str):
            names = [names]
        file_names = {
            example_name: file_list
            for example_name, file_list in file_names.items()
            if example_name in names
        }
    return list(Example(name, files) for name, files in file_names.items())


def validate_args(args: StrListStr) -> list[str]:
    """convert args to list of strings"""
    if isinstance(args, str):
        args = [args]
    elif args is None:
        args = []
    return args


def run_script(filename: str | Path, args: StrListStr = None) -> Result:
    """run script"""
    args = validate_args(args)
    if not Path(filename).exists():
        return Result("", "")
    res = subprocess.run(
        ["python", filename, *args],
        capture_output=True,
        check=False,
    )

    return Result(
        res.stdout.decode("utf-8"), res.stderr.decode("utf-8"), res.returncode
    )


def run_module(
    module_name: str,
    args: list[str] = [],
    check: bool = False,
    cwd: Path | None = None,
) -> Result:
    """run module"""
    res = subprocess.run(
        ["python", "-m", module_name, *args],
        capture_output=True,
        check=check,
        cwd=cwd,
    )
    return Result(
        res.stdout.decode("utf-8"), res.stderr.decode("utf-8"), res.returncode
    )


def get_args(
    name: str,
    cfg: Cfg | None = None,
) -> list[Args]:
    """get script args from file"""
    cfg = Cfg() if cfg is None else cfg
    args_filename = Path(
        cfg.examples_path,
        cfg.results_path,
        f"{name}{cfg.split}{cfg.args_filename_suffix}.txt",
    )
    if not args_filename.exists():
        return []
    with open(args_filename, "r", encoding="utf-8") as file:
        lines = [
            line.split("#", maxsplit=1)[0].rstrip().split(":", maxsplit=1)
            for line in file.readlines()
            if line != "\n" and not line.startswith("#")
        ]
    return [
        Args(item[0], item[1].split() if len(item) == 2 else None) for item in lines
    ]


def write_result(
    name: str,
    result: Result,
    args: Args,
    cfg: Cfg | None = None,
) -> None:
    """write result to file"""
    cfg = Cfg() if cfg is None else cfg
    result_filename = Path(
        cfg.examples_path,
        cfg.results_path,
        f"{name}{cfg.split}{args.name}.txt",
    )
    print(f"  {name}: {args.name}, filename: {result_filename}")
    with open(result_filename, "w", encoding="utf-8") as file:
        args_repr = " " + ", ".join(args.list) if args.list else ""
        file.write(f"# result for run {name} with args:{args_repr}\n")
        file.write(f"# stdout\n{result.stdout}# stderr\n{result.stderr}")


def write_examples(
    names: str | List[str] | None = None,
    cfg: Cfg | None = None,
) -> None:
    """write examples results to file"""
    cfg = Cfg() if cfg is None else cfg
    examples: list[Example] = get_examples(cfg=cfg, names=names)
    for example in examples:
        print(f"Writing results for {example.name}")
        args_list = get_args(example.name, cfg)
        for args in args_list:
            write_result(
                example.name,
                run_script(example.files[0], args.list),
                args,
                cfg,
            )


def read_result(name: str, arg_name: str, cfg: Cfg | None = None) -> Result:
    """read result from file, return stdout and stderr.
    If not found, return empty strings
    """
    cfg = Cfg() if cfg is None else cfg
    result_filename = Path(
        cfg.examples_path,
        cfg.results_path,
        f"{name}{cfg.split}{arg_name}.txt",
    )
    if not result_filename.exists():
        return Result("", "")
    with open(result_filename, "r", encoding="utf-8") as file:
        text = file.read()
    res, err = text.split("# stdout\n")[1].split("# stderr\n")
    return Result(res, err)


def check_examples(
    names: str | List[str] | None = None,
    cfg: Cfg | None = None,
) -> List[ExampleError] | None:
    """Runs examples, compare results with saved"""
    cfg = Cfg() if cfg is None else cfg
    examples = get_examples(cfg=cfg, names=names)
    errors_dict: dict[str, list[Error]] = defaultdict(list)
    for example_name, file_list in examples:
        errors = run_check_example(example_name, file_list, cfg=cfg)
        if errors:
            errors_dict[example_name].extend(errors)
    if errors_dict:
        return list(ExampleError(name, errors) for name, errors in errors_dict.items())
    return None


def run_check_example(
    example_name: str,
    file_list: List[Path],
    cfg: Cfg | None = None,
) -> List[Error] | None:
    """Run and check example"""
    cfg = Cfg() if cfg is None else cfg
    args_list = get_args(example_name, cfg)
    errors: list[Error] = []
    for args in args_list:
        for file in file_list:
            result = run_script(file, args.list)
            expected = read_result(example_name, args.name, cfg)
            for res, exp in zip(result[:2], expected[:2]):
                if res != exp:
                    if not usage_equal_with_replace(
                        res,
                        exp,
                    ):
                        errors.append(Error(args.name, str(file), res, exp))

    return errors or None


def split_usage(res: str) -> Tuple[str, str]:
    """Split result to usage (as one line) and other."""
    split = res.split("\n\n", maxsplit=1)
    if len(split) == 1:
        usage, other = res, ""
    else:
        usage, other = split[0], split[1]
    return " ".join(line.strip() for line in usage.split("\n")), other


def get_prog_name(usage: str) -> str:
    """Get prog name"""
    if usage.startswith("usage: "):
        return usage.split("usage: ", maxsplit=1)[1].split(" ", maxsplit=1)[0]
    return ""


def replace_prog_name(usage: str, usage_expected: str) -> str:
    """Replace prog name"""
    prog_name = get_prog_name(usage)
    expected_name = get_prog_name(usage_expected) or prog_name
    return usage.replace(prog_name, expected_name)


def usage_equal_with_replace(
    res: str,
    expected_res: str,
) -> bool:
    """Check if usage and after replace result is equal to expected"""
    if res.startswith("usage:"):
        usage, other = split_usage(res)
        usage_expected, other_expected = split_usage(expected_res)
        usage_replaced = replace_prog_name(usage, usage_expected)
        if usage_replaced != usage_expected:
            return replace_py_less310(usage_replaced, usage_expected)
        else:
            if other == other_expected:
                return True
            if ARGPARSE_OLD and replace_py_less310(
                other, other_expected
            ):  # pragma: no cover
                return True
    return False


def replace_py_less310(text: str, expected: str) -> bool:
    """Replace text used in python less 3.10"""
    replaced = text.replace("optional arguments", "options")
    if replaced == expected:
        return True
    expected_replaced = re.sub(r"argument \{(.*)\}: ", "", expected)
    if replaced == expected_replaced:
        return True
    return False
