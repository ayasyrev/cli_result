""" Test for run scripts and compare output with expected results.
"""
from __future__ import annotations
import re
import sys

import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Union

StrListStr = Union[str, List[str], None]
PathStr = Union[str, Path, None]


ARGPARSE_OLD = sys.version_info.minor < 10


@dataclass
class Cfg:
    """base config for cli_result"""

    examples_path: str = "examples"
    results_path: str = "results"
    args_filename_suffix: str = "args"
    split: str = "__"


def get_examples(
    names: str | List[str] | None = None,
    cfg: Cfg = None,
) -> List[Tuple[str, list[Path]]]:
    """get examples names"""
    if cfg is None:
        cfg = Cfg()
    file_names: Dict[str, List[str]] = defaultdict(list)
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
    return list((name, files) for name, files in file_names.items())


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
    if not Path(filename).exists():
        return "", ""
    res = subprocess.run(
        ["python", filename, *args],
        capture_output=True,
        check=False,
    )

    return res.stdout.decode("utf-8"), res.stderr.decode("utf-8")


def get_args(
    name: str,
    cfg: Cfg = None,
) -> dict[str, str]:
    """get script args from file"""
    if cfg is None:
        cfg = Cfg()
    args_filename = Path(
        cfg.examples_path,
        cfg.results_path,
        f"{name}{cfg.split}{cfg.args_filename_suffix}.txt",
    )
    if not args_filename.exists():
        return {}
    with open(args_filename, "r", encoding="utf-8") as file:
        lines = [
            line.split("#", maxsplit=1)[0].rstrip().split(":", maxsplit=1)
            for line in file.readlines()
            if line != "\n" and not line.startswith("#")
        ]
    return {item[0]: item[1].split() if len(item) == 2 else None for item in lines}


def write_result(
    name: str,
    stdout: str,
    stderr: str,
    arg_name: str,
    args: list[str] | None = None,
    cfg: Cfg = None,
) -> None:
    """write result to file"""
    if cfg is None:  # pragma: no cover
        cfg = Cfg()
    if args is None:
        args = []
    result_filename = Path(
        cfg.examples_path,
        cfg.results_path,
        f"{name}{cfg.split}{arg_name}.txt",
    )
    # if not result_filename.parent.exists():
    #     result_filename.parent.mkdir(parents=True)
    print(f"  {name}: {args}, filename: {result_filename}")
    with open(result_filename, "w", encoding="utf-8") as file:
        file.write(f"# result for run {name} with args: {', '.join(args)}\n")
        file.write(f"# stdout\n{stdout}# stderr\n{stderr}")


def write_examples(
    examples: str | List[str] | None = None,
    cfg: Cfg = None,
) -> None:
    """write experiments results to file"""
    if cfg is None:  # pragma: no cover
        cfg = Cfg()
    examples = get_examples(cfg=cfg, names=examples)
    for example_name, filenames in examples:
        print(f"Writing results for {example_name}")
        name_args = get_args(example_name, cfg)
        for name, args in name_args.items():
            write_result(
                example_name,
                *run_script(filenames[0], args),
                name,
                args,
                cfg,
            )


def read_result(name: str, arg_name: str, cfg: Cfg = None) -> tuple[str, str]:
    """read result from file, return stdout and stderr.
    If not found, return empty strings
    """
    if cfg is None:
        cfg = Cfg()
    result_filename = Path(
        cfg.examples_path,
        cfg.results_path,
        f"{name}{cfg.split}{arg_name}.txt",
    )
    if not result_filename.exists():
        return "", ""
    with open(result_filename, "r", encoding="utf-8") as file:
        text = file.read()
    res, err = text.split("# stdout\n")[1].split("# stderr\n")
    return res, err


def check_examples(
    names: str | List[str] | None = None,
    cfg: Cfg = None,
) -> List[Tuple[str, List[str]]] | None:
    """Runs examples, compare results with saved"""
    if cfg is None:
        cfg = Cfg()
    experiments = get_examples(cfg=cfg, names=names)
    results = defaultdict(Dict[str, List[str]])
    for experiment_name, file_list in experiments:
        errors = run_check_example(experiment_name, file_list, cfg=cfg)
        if errors:
            results[experiment_name] = errors
    if results:
        return list((name, errors) for name, errors in results.items())
    return None


def run_check_example(
    experiment_name: str,
    file_list: List[Path],
    cfg: Cfg | None = None,
) -> List[Tuple[str, str]]:
    """Run and check example"""
    if cfg is None:
        cfg = Cfg()  # pragma: no cover  checked from run_examples
    name_args = get_args(experiment_name, cfg)
    errors = defaultdict(list)
    for name, args in name_args.items():
        for file in file_list:
            res, err = run_script(file, args)
            expected_res, expected_err = read_result(experiment_name, name, cfg)
            if res != expected_res:
                if not usage_equal_with_replace(
                    res,
                    expected_res,
                ):
                    errors[name].append((str(file), [res, expected_res]))
            if err != expected_err:
                if not usage_equal_with_replace(
                    err,
                    expected_err,
                ):
                    errors[name].append((str(file), [err, expected_err]))
    if errors:
        return list((name, err_list) for name, err_list in errors.items())
    return None


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
            if (
                ARGPARSE_OLD and replace_py_less310(other, other_expected)
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
