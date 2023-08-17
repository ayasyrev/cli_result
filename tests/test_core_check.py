from cli_result.core import Cfg, check_examples


def test_check_examples():
    """test check_examples"""
    # no args
    results = check_examples()
    assert results is None

    # default config
    results = check_examples()
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
