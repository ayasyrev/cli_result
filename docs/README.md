# Cli_results

Simple lib to test results or script runs from command line.  

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cli_result)](https://pypi.org/project/cli_result/)
[![PyPI version](https://img.shields.io/pypi/v/cli_result?color=blue)](https://pypi.org/project/cli_result/)  
[![Tests](https://github.com/ayasyrev/cli_result/workflows/Tests/badge.svg)](https://github.com/ayasyrev/cli_result/actions?workflow=Tests)  [![Codecov](https://codecov.io/gh/ayasyrev/cli_result/branch/main/graph/badge.svg)](https://codecov.io/gh/ayasyrev/cli_result)  

# Install

Install from pypi:  

`pip install cli_result`

Or install from github repo:

`pip install git+https://github.com/ayasyrev/cli_result.git`

# Usage.

Main purpose test results of examples run. We run all scripts in examples folder and compare results with expected results. Check it at different python versions.  
So we can be sure that all scripts work and has similar behaviors in different python versions.  
It's not suitable to run script that supposed to run for a long time or resources are limited.  
But it's good for quick tests, to check configs and shorts demos (examples).

Put your script in examples folder and expected results in results folder.  
Arguments for tests at file name same as script name + `__args.txt.`


```python
from cli_result.core import check_examples, Cfg
```


```python
result = check_examples()
```

This run all scripts in examples folder with arguments from `__args.txt.` file and compare with results at `results/` folder.  


```python
assert result is None
```
