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


cfg = Cfg(examples_path="examples/")
examples = get_examples(cfg=cfg)


@pytest.mark.parametrize("example_name, file_list", examples)
def test_run_check_example(example_name, file_list):
    """test run_check_example"""
    results = run_check_example(example_name, file_list, cfg=cfg)
    assert results is None


cfg = Cfg(examples_path="examples/examples_extra")
examples = get_examples(cfg=cfg)


@pytest.mark.parametrize("example_name, file_list", examples)
def test_run_check_example_extra(example_name, file_list):
    """test run_check_example"""
    results = run_check_example(example_name, file_list, cfg=cfg)
    assert results is None


cfg = Cfg(examples_path="tests/examples/examples_errors")
examples = get_examples(cfg=cfg)


@pytest.mark.parametrize("example_name, file_list", examples)
def test_run_check_examples_errors(example_name, file_list):
    """test check_examples with errors"""
    # errors
    results = run_check_example(example_name, file_list, cfg=cfg)
    assert results


def test_check_examples_errors():
    """test check_examples with errors"""
    # errors
    results = check_examples(cfg=cfg)
    assert results
