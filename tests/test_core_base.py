import shutil
import sys
from pathlib import Path

from cli_result.core import (
    Cfg,
    check_examples,
    usage_equal_with_replace,
    get_args,
    get_examples_names,
    get_prog_name,
    read_result,
    replace_prog_name,
    run_script,
    split_usage,
    validate_args,
    write_examples,
    write_result,
)

VERSION_LESS_10 = sys.version_info.minor < 10

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
    example_1 = examples[0]
    assert example_1[0] == "example_1"
    assert example_1[1][0] == Path("examples/example_1.py")

    # filter examples
    example_name = "example_1"
    examples = get_examples_names(names=example_name)
    assert len(examples) == 1
    example_1 = examples[0]
    assert example_1[0] == "example_1"
    assert example_1[1][0] == Path("examples/example_1.py")

    example_name_list = ["example_1"]
    examples = get_examples_names(names=example_name_list)
    assert len(examples) == 1
    example_1 = examples[0]
    assert example_1[0] == "example_1"
    assert example_1[1][0] == Path("examples/example_1.py")

    # wrong name
    example_name = "example_wrong"
    examples = get_examples_names(names=example_name)
    assert len(examples) == 0

    # different folder
    cfg = Cfg(examples_path="examples/examples_extra")
    examples = get_examples_names(cfg=cfg)
    assert len(examples) == 1
    example_1 = examples[0]
    assert example_1[0] == "example_extra_1"
    assert example_1[1][0] == Path("examples/examples_extra/example_extra_1.py")
    assert len(example_1[1]) == 2


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
    example = examples[0]
    name = example[0]
    assert name == "example_1"
    filename = example[1][0]
    assert Path(filename).exists()

    res, err = run_script(filename)
    expected = read_result(name, "no_args")
    assert res == expected[0]
    assert err == expected[1]

    res, err = run_script(filename, "--help")
    expected = read_result(name, "help")
    assert res == expected[0] or usage_equal_with_replace(
        res,
        expected[0],
    )
    assert err == expected[1]

    # file not exist
    res, err = run_script("wrong_name")
    assert res == ""
    assert err == ""


def test_split_usage():
    """test split_usage"""
    res = "usage: example_1.py [-h]\n\nsome text"
    expected_res = "usage: example_1.py [-h]", "some text"
    usage, other = split_usage(res)
    assert usage == expected_res[0]
    assert other == expected_res[1]

    res = "usage: example_1.py [-h] arg_1\n   arg_2\n\nsome text"
    expected_usage = "usage: example_1.py [-h] arg_1 arg_2"
    expected_other = "some text"
    usage, other = split_usage(res)
    assert usage == expected_usage
    assert other == expected_other

    # no \n\n - error case/ all text is usage - remove \n
    res = "usage: example_1.py [-h] arg_1\n   arg_2\nsome text"
    # res = "usage: example_1.py [-h]\n:example_1.py: error: unrecognized arguments:"
    usage, other = split_usage(res)
    assert usage == expected_usage + " some text"
    assert other == ""

    # wrong usage
    text = ""
    assert split_usage(text) == ("", "")


def test_get_prog_name():
    """test get_prog_name"""
    usage = "usage: example_1.py [-h] arg_1"
    expected_res = "example_1.py"
    assert get_prog_name(usage) == expected_res

    # if expected not usage
    usage = "not usage: example_1.py [-h] arg_1"
    expected_res = ""
    assert get_prog_name(usage) == expected_res


def test_replace_prog_name():
    """test replace_prog_name"""
    usage = "usage: example_2.py [-h] arg_1"
    usage_expected = "usage: example_1.py [-h] arg_1"
    assert replace_prog_name(usage, usage_expected) == usage_expected

    usage = "usage: my_app [-h] arg_1"
    usage_expected = "usage: example_1.py [-h] arg_1"
    assert replace_prog_name(usage, usage_expected) == usage_expected

    # expected not usage
    usage = "usage: my_app [-h] arg_1"
    usage_expected = "some text"
    assert replace_prog_name(usage, usage_expected) == usage


def test_equal_with_replace():
    """test equal_with_replace"""
    res = "usage: example_02.py [-h]\n\nsome text"
    expected_res = "usage: example_01.py [-h]\n\nsome text"
    assert usage_equal_with_replace(res, expected_res)

    res = "usage: example_02.py [-h]\n\noptional arguments: some options"
    expected_res = "usage: example_01.py [-h]\n\noptions: some options"

    if VERSION_LESS_10:
        assert usage_equal_with_replace(res, expected_res)

    # # false
    res = "usage: example_02.py [-h]\n\noptional arguments: wrong options"
    expected_res = "usage: example_01.py [-h]\n\noptions: some options"
    if VERSION_LESS_10:
        assert not usage_equal_with_replace(res, expected_res)

    res = "usage: example_02.py [-h]\n\nnoptions: wrong options"
    expected_res = "usage: example_01.py [-h]\n\noptions: some options"
    assert not usage_equal_with_replace(res, expected_res)


def test_check_examples():
    """test check_examples"""
    # no args
    results = check_examples()
    assert results is None

    # default config
    cfg = Cfg()
    results = check_examples(cfg=cfg)
    assert results is None

    # extra
    cfg = Cfg(examples_path="examples/examples_extra")
    results = check_examples(cfg=cfg)
    assert results is None


def test_check_examples_errors():
    """test check_examples with errors"""
    # errors
    cfg = Cfg(examples_path="tests/examples/examples_errors")
    results = check_examples(cfg=cfg)
    assert results


def test_write_experiments(tmp_path: Path):
    """test write_experiments"""
    cfg = Cfg(examples_path=tmp_path)

    examples_path = Path("tests/examples")
    results_path = examples_path / cfg.results_path
    example_fn = "exmpl_1.py"
    example_args_fn = "exmpl_1__args.txt"

    # create tmp example folder w/ experiment
    test_example = tmp_path / example_fn
    shutil.copy(examples_path / example_fn, test_example)
    assert test_example.exists()

    assert (results_path / example_args_fn).exists()
    test_results_path = tmp_path / cfg.results_path
    test_results_path.mkdir()
    shutil.copy(results_path / example_args_fn, test_results_path / example_args_fn)
    assert (tmp_path / "results" / "exmpl_1__args.txt").exists()

    write_examples(cfg)
    res_files = list(results_path.glob("*.txt"))
    test_results_files = list(test_results_path.glob("*.txt"))
    assert len(res_files) == len(test_results_files)
    for file in res_files:
        with open(file, "r", encoding="utf-8") as fh:
            res = fh.read()
        with open(test_results_path / file.name, "r", encoding="utf-8") as fh:
            test = fh.read()
        if VERSION_LESS_10:
            assert test.replace("optional arguments", "options") == res
        else:
            assert res == test

    # single result
    example_name = "example_name"
    arg_name = "arg_name"
    args = ["arg1", "arg2"]
    write_result(example_name, "res", "err", arg_name, args, cfg)
    result_file = test_results_path / f"{example_name}{cfg.split}{arg_name}.txt"
    assert result_file.exists()
    res, err = read_result(example_name, arg_name, cfg)
    assert res == "res"
    assert err == "err"
    with open(result_file, "r", encoding="utf-8") as fh:
        first_line = fh.readline()
    assert first_line.split("args: ", maxsplit=1)[1] == "arg1, arg2\n"

    # no args
    arg_name = "no_arg"
    write_result(example_name, "res", "err", arg_name, cfg=cfg)
    result_file = test_results_path / f"{example_name}{cfg.split}{arg_name}.txt"
    assert result_file.exists()
    res, err = read_result(example_name, arg_name, cfg)
    assert res == "res"
    assert err == "err"
    with open(result_file, "r", encoding="utf-8") as fh:
        first_line = fh.readline()
    assert first_line.split("args: ", maxsplit=1)[1].rstrip() == ""
