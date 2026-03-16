# Python extensions for Daisy

## Installation
Clone the repository and install it in your Daisy python environment
```
git clone https://github.com/daisy-model/python-extensions.git
cd python-extensions
daisy --pip install -e .
```
Because it is installed as an editable package with the `-e` flag, any changes in the repository will be available in Daisy.

## Creating a new extension
Extensions are organized in subdirectories under `daisy_extension`. To create a new extension add your python files under the relevant subdirectory. If there is no relevant subdirectory add a new subdirectory with an empty `__init__.py` file and add your python files to this directory.

For example, if you want to a chemical reaction named `my_new_reaction.py` you should have directory layout that looks like

```
daisy_extensions/
└── reactions
    ├── __init__.py
    └── my_new_reaction.py
```

Once you are happy with your extension you should create a test for it and add it to the relevant subdirectory under the `tests` directory. Continuing with the reaction example from above, you should have a directory layout that looks like
```
./
├── daisy_extensions
│   └── reactions
│       ├── __init__.py
│       └── my_new_reaction.py
├── LICENSE
├── pyproject.toml
├── README.md
└── tests
    └── reactions
        └── test_my_new_reaction.py
```
You should write tests that directly call the python function and tests that run daisy.

You can use the `default_denitrification` example as a starting point
```
├── daisy_extensions
│   └── reactions
│       ├── default_denitrification.py
└── tests
    └── reactions
        ├── test-data
        │   ├── default-denitrification-args-and-targets.csv
        │   ├── default-denitrification.dai
        │   ├── expected-default-denitrification.csv
        ├── test_default_denitrification.py
```


### Dependencies
If your extension has any external dependencies you should add them to the `pyproject.toml` under `dependencies`. We recommend using [uv](https://docs.astral.sh/uv/) for this. For example, to add `numpy` and `pandas`
```
uv add numpy pandas
```

The simplest way to install these dependencies in your Daisy environment is to reinstall the `python-extensions` package with
```
daisy --pip install -e .
```

### Sharing
If you want to share your extensions with others you can create a pull request to have it included in this repository. First you need to lint and test your code. We recommend using [uv](https://docs.astral.sh/uv/) to lint and test.

#### Linting
```
uv run pylint .
```
Your code should be rated 10/10. If you need to disable linting for parts of your code be as specific as possible. For example, to disable [too-many-arguments](https://pylint.pycqa.org/en/latest/user_guide/messages/refactor/too-many-arguments.html) for a function, you should do it inside the function
```
def some_function(a, b, c, d, e, f, g):
    # pylint: disable=too-many-argument
    ...
```

If you don't want to use `uv`, you can use pip
```
pip install pylint
pylint .
```

#### Testing
```
uv run pytest --cov=daisy_extensions tests
```
Ensure that your test passes and that your extension has 100% coverage. If for some reason it is not possible to get 100% coverage, document it clearly.

If you don't want to use `uv`, you can use pip
```
pip install pytest pytest-cov
pytest --cov=daisy_extensions tests
```
