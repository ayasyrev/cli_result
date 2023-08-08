from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Union


StrListStr = Union[str, list[str], None]
PathStr = Union[str, Path, None]


@dataclass
class Cfg:
    """base config for cli_result"""

    examples_path = "examples"
    results_path = "results"
    args_filename_suffix = "args"
    split = "__"


def get_examples_names(
    cfg: Cfg = None,
) -> dict[str, list[Path]]:
    """get examples names"""
    if cfg is None:
        cfg = Cfg()
    examples_names = defaultdict(list)
    for filename in Path(cfg.examples_path).glob("*.py"):
        example_name = filename.stem.split(cfg.split)[0]
        if example_name == filename.stem:
            examples_names[example_name].insert(0, filename)
        else:
            examples_names[example_name].append(filename)
    return examples_names


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
    with open(args_filename, "r", encoding="utf-8") as file:
        lines = [
            line.split(": ", maxsplit=1)
            for line in file.readlines()
            if line != "\n" and not line.startswith("#")
        ]
    return {item[0]: item[1].split() for item in lines}


def write_result(
    name: str,
    stdout: str,
    stderr: str,
    arg_name: str,
    args: list[str] | None,
    cfg: Cfg = None,
) -> None:
    """write result to file"""
    if cfg is None:
        cfg = Cfg()
    if args is None:
        args = []
    result_filename = Path(
        cfg.examples_path,
        cfg.results_path,
        f"{name}{cfg.split}{arg_name}.txt",
    )
    if not result_filename.parent.exists():
        result_filename.parent.mkdir(parents=True)
    with open(result_filename, "w", encoding="utf-8") as file:
        file.write(f"# result for run {name} with args: {', '.join(args)}\n")
        file.write(f"# stdout\n{stdout}# stderr\n{stderr}")


def write_experiments(
    cfg: Cfg = None,
) -> None:
    """write experiments results to file"""
    if cfg is None:
        cfg = Cfg()
    experiments = get_examples_names(cfg.example_path)
    for experiment_name, filenames in experiments.items():
        name_args = get_args(experiment_name)
        for name, args in name_args.items():
            write_result(
                experiment_name,
                *run_script(filenames[0], args),
                name,
                args,
                cfg,
            )


def read_result(name: Path, arg_name: str, cfg: Cfg = None) -> tuple[str, str]:
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


def test_examples(
    cfg: Cfg = None,
) -> dict[str : dict[str, str]]:
    """Runs examples, compare results with saved"""
    if cfg is None:
        cfg = Cfg()
    experiments = get_examples_names(cfg)
    results = defaultdict(dict[str, list[str]])
    for experiment_name, filenames in experiments.items():
        name_args = get_args(experiment_name)
        errors = defaultdict(list)
        for name, args in name_args.items():
            for filename in filenames:
                res, err = run_script(filename, args)
                expected_res, expected_err = read_result(experiment_name, name, cfg)
                if (
                    res != expected_res
                    and res.replace(filename.stem, experiment_name) != expected_res
                ):
                    errors[name].append({filename: [res, expected_res]})
                if (
                    err != expected_err
                    and err.replace(filename.stem, experiment_name) != expected_err
                ):
                    errors[name].append({filename: [err, expected_err]})
        if errors:
            results[experiment_name] = errors
    return results
