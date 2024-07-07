# Cli_results

Simple lib to test results or script runs from command line.

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cli_result)](https://pypi.org/project/cli_result/)
[![PyPI version](https://img.shields.io/pypi/v/cli_result?color=blue)](https://pypi.org/project/cli_result/)
[![Tests](https://github.com/ayasyrev/cli_result/workflows/Tests/badge.svg)](https://github.com/ayasyrev/cli_result/actions?workflow=Tests)  [![Codecov](https://codecov.io/gh/ayasyrev/cli_result/branch/main/graph/badge.svg)](https://codecov.io/gh/ayasyrev/cli_result)

## Install

Install from pypi:

`pip install cli_result`

Or install from github repo:

`pip install git+https://github.com/ayasyrev/cli_result.git`

## Usage.

Main purpose test results of examples run. We run all scripts in examples folder and compare results with expected results. Check it at different python versions.
So we can be sure that all scripts work and has similar behaviors in different python versions.
It's not suitable to run script that supposed to run for a long time or resources are limited.
But it's good for quick tests, to check configs and shorts demos (examples).

Put your script in examples folder and expected results in results folder.
Arguments for tests at file name same as script name + `__args.txt.`


```python
from cli_result import check_examples, Cfg
```


```python
errors = check_examples()
```

This run all scripts in examples folder with arguments from `__args.txt` file and compare with results at `results/` folder.


```python
assert errors is None
```

## Examples

We can change examples folder.


```python
cfg = Cfg(examples_path="../examples/examples_extra/")
```

Check examples at folder:


```python
from cli_result import get_examples

examples = get_examples(cfg=cfg)
```

We got list of examples as named tuple example_name, files


```python
example = examples[0]
# name
print(example.name)  # or example[0]
# files
print(example.files[0])
print(example[1][1])
```
<details open> <summary>output</summary>
<pre>
example_extra_1
../examples/examples_extra/example_extra_1.py
../examples/examples_extra/example_extra_1__alter.py
</pre>
</details>

## Run script

We can run script and look at result.


```python
from cli_result import  run_script

result = run_script(
    filename=example[1][0],
    args="--help",
)
```


```python
print(result.stdout)
```
<details open> <summary>output</summary>
<pre>
usage: example_extra_1.py [-h] [--echo ECHO]

options:
    -h, --help   show this help message and exit
    --echo ECHO
</pre>
</details>


```python
assert result.stderr == ""
```

## Load expected result.


```python
from cli_result import read_result, get_args
```

Load arguments for example.
`get_args` returns list of `Args`


```python
args = get_args(example.name, cfg)

print(args[0])
```
<details open> <summary>output</summary>
<pre>
Args(name='help', list=['--help'])
</pre>
</details>


```python
expected = read_result(
    name=example.name,
    arg_name=args[0].name,  # or args[0][0]
    cfg=cfg,
)
```

Now we can compare results.


```python
assert result == expected
```

## Check one example.

We can check one example.


```python
from cli_result import run_check_example

errors = run_check_example(
    example_name=example.name,
    file_list=example.files,
    cfg=cfg,
)
assert errors is None
```

Alternatively we can check one as:


```python
errors = check_examples(
    names=example.name,  # we can send list of names as [name1, name2, ...]
    cfg=cfg,
)
assert errors is None
```

## Check all examples.

Or check all examples.


```python
errors = check_examples(cfg=cfg)
assert errors is None
```

## Check errors

Lets look at example with error.


```python
cfg = Cfg(examples_path="../tests/examples/examples_errors/")

errors = check_examples(cfg=cfg)
assert errors is not None
print(f"Examples with errors: {len(errors)}, {examples[0].name}: {len(errors[0].list)} errors")
```
<details open> <summary>output</summary>
<pre>
Examples with errors: 1, example_extra_1: 10 errors
</pre>
</details>

Let look at one of errors.
We got file name that has error, result of run and expected result. Now we can look for what is wrong.


```python
example_error = errors[0]
print(example_error.name)
```
<details open> <summary>output</summary>
<pre>
example_1
</pre>
</details>


```python
error = example_error.list[4]
print(error.argname)
print(error.filename)
```
<details open> <summary>output</summary>
<pre>
empty_str
../tests/examples/examples_errors/example_1__err_1.py

</pre>
</details>

We can compare result with expected result.


```python
print(error.res)
```
<details open> <summary>output</summary>
<pre>
usage: example_1__err_1.py [-h] [--e E]
example_1__err_1.py: error: unrecognized arguments: ""
</pre>
</details>

And expected is:


```python
print(error.exp)
```
<details open> <summary>output</summary>
<pre>
usage: example_1.py [-h] [--echo ECHO]
example_1.py: error: unrecognized arguments: ""
</pre>
</details>
