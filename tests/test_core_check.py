import pytest

from cli_result.core import Cfg, check_examples, get_examples, run_check_example


def test_check_examples():
    """test check_examples"""
    # no args
    results = check_examples()
    assert results is None

    # extra
    examples_path = "examples/examples_extra"
    results = check_examples(cfg=Cfg(examples_path=examples_path))
    assert results is None


cfg_base = Cfg(examples_path="examples/")
examples_base = get_examples(cfg=cfg_base)


@pytest.mark.parametrize("example_name, file_list", examples_base)
def test_run_check_example(example_name, file_list):
    """test run_check_example"""
    results = run_check_example(example_name, file_list, cfg=cfg_base)
    assert results is None


cfg_extra = Cfg(examples_path="examples/examples_extra")
examples_extra = get_examples(cfg=cfg_extra)


@pytest.mark.parametrize("example_name, file_list", examples_extra)
def test_run_check_example_extra(example_name, file_list):
    """test run_check_example"""
    results = run_check_example(example_name, file_list, cfg=cfg_extra)
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
