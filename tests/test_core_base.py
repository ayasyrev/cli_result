from pathlib import Path
import subprocess

from cli_result.core import (
    Cfg,
    get_args,
    get_examples_names,
    read_result,
    run_script,
    test_examples,
    validate_args,
)


HELP_RES = """usage: example_1.py [-h] [--echo ECHO]

options:
  -h, --help   show this help message and exit
  --echo ECHO
"""


def test_validate_args():
    """test validate_args"""
    # string arg
    result = validate_args("hello")
    assert result == ["hello"]

    # multiple args
    result = validate_args(["hello", "world"])
    assert result == ["hello", "world"]

    # empty args
    result = validate_args(None)
    assert result == []


def test_get_examples_names():
    """test get_examples_names"""
    examples = get_examples_names()
    assert len(examples) == 1
    example_1 = list(examples.keys())[0]
    assert example_1 == "example_1"
    assert examples[example_1][0] == Path("examples/example_1.py")

    # different folder
    cfg = Cfg(examples_path="examples/examples_extra")
    examples = get_examples_names(cfg)
    assert len(examples) == 1
    example_1 = list(examples.keys())[0]
    assert example_1 == "example_extra_1"
    assert examples[example_1][0] == Path(
        "examples/examples_extra/example_extra_1.py"
    )
    assert len(examples[example_1]) == 2


def test_get_args():
    """test get_args"""
    # args file not exists
    args = get_args("wrong_name")
    assert args == {}

    # base
    args = get_args("example_1")
    expected_res = {
        "help": ["--help"],
        "no_args": [],
        "empty_str": ['""'],
        "short_flag_help": ["-h"],
        "positional": ["cl_arg"],
        "optional": ["--echo", "cl_arg"],
    }
    assert args == expected_res

    # different folder
    cfg = Cfg(examples_path="examples/examples_extra")
    args = get_args("example_extra_1", cfg)
    assert args == expected_res


def test_read_result():
    """test read_result"""
    name_1 = "example_1"
    arg_name = "help"
    res, err = read_result(name_1, arg_name)
    assert res == HELP_RES
    assert err == ""

    # wrong name
    res, err = read_result("wrong_name", arg_name)
    assert res == ""
    assert err == ""

    # wrong filename
    cfg = Cfg(examples_path="examples/examples_extra")
    res, err = read_result(name_1, arg_name, cfg)
    assert res == ""
    assert err == ""
    # extra
    name_2 = "example_extra_1"
    res, err = read_result(name_2, arg_name, cfg)
    assert res == HELP_RES.replace(name_1, name_2)
    assert err == ""


def test_run_script():
    """test run_script"""
    examples = get_examples_names()
    name = list(examples.keys())[0]
    assert name == "example_1"
    filename = examples[name][0]
    assert Path(filename).exists()

    res, err = run_script(filename)
    expected = read_result(name, "no_args")
    assert res == expected[0]
    assert err == expected[1]

    res, err = run_script(filename, "--help")
    expected = read_result(name, "help")
    assert res == expected[0]
    assert err == expected[1]

    # file not exist
    res, err = run_script("wrong_name")
    assert res == ""
    assert err == ""


def test_test_examples():
    """test test_examples"""
    cfg = Cfg()
    results = test_examples(cfg)
    assert not results

    # extra
    cfg = Cfg(examples_path="examples/examples_extra")
    results = test_examples(cfg)
    assert not results
