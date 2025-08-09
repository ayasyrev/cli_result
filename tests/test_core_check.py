import pytest

from cli_result.core import (
    Cfg,
    check_examples,
    get_args,
    get_examples,
    run_check_example,
    replace_remove_quotes,
    replace_add_quotes,
)


def test_check_examples():
    """test check_examples"""
    # no args
    results = check_examples()
    assert results is None


def test_check_examples_extra():
    # extra
    examples_path = "examples/examples_extra"
    results = check_examples(cfg=Cfg(examples_path=examples_path))
    assert results is None


cfg_base = Cfg(examples_path="examples/")
examples_base = get_examples(cfg=cfg_base)
examples_base_with_args = []
for example_name, file_list in examples_base:
    for file in file_list:
        # add args
        args = get_args(example_name, cfg_base)
        for arg in args:
            examples_base_with_args.append((example_name, [file], arg))


@pytest.mark.parametrize("example_name, file_list, arg", examples_base_with_args)
def test_run_check_example(example_name, file_list, arg):
    """test run_check_example"""
    results = run_check_example(example_name, file_list, arg=arg, cfg=cfg_base)
    if results is None:
        return
    # here we have 1 error
    assert len(results) == 1
    error = results[0]
    replaced = replace_remove_quotes(error.res)
    # replaced = replace_add_quotes(error.res)
    # # if replaced equal expected it cant be error here
    # assert replaced == error.exp
    assert error.res == error.exp


cfg_extra = Cfg(examples_path="examples/examples_extra")
examples_extra = get_examples(cfg=cfg_extra)
examples_with_args = []
for example_name, file_list in examples_extra:
    for file in file_list:
        # add args
        args = get_args(example_name, cfg_extra)
        for arg in args:
            examples_with_args.append((example_name, [file], arg))


@pytest.mark.parametrize("example_name, file_list, arg", examples_with_args)
def test_run_check_example_extra(example_name, file_list, arg):
    """test run_check_example"""
    results = run_check_example(example_name, file_list, arg=arg, cfg=cfg_extra)
    assert results is None


cfg_errors = Cfg(examples_path="tests/examples/examples_errors")
examples_errors = get_examples(cfg=cfg_errors)


@pytest.mark.parametrize("example_name, file_list", examples_errors)
def test_run_check_examples_errors(example_name, file_list):
    """test check_examples with errors"""
    # errors
    results = run_check_example(example_name, file_list, cfg=cfg_errors)
    assert results


def test_check_examples_errors():
    """test check_examples with errors"""
    # errors
    results = check_examples(cfg=cfg_errors)
    assert results
