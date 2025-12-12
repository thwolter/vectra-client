# Installation

The client ships as a standard Python package requiring **Python 3.13+**. Use your preferred environment manager and install from the repository root:

```bash
pip install .
```

For editable installs during development:

```bash
pip install -e .[dev]
```

Dependencies include `httpx`, `langchain-core`, `nexor`, `pydantic`, and the private `tenauth` helper referenced in `pyproject.toml`. Dev dependencies add linters, test runners, and related tooling (see `pyproject.toml` `dependency-groups.dev`).

If you pull the library as a dependency in another project, install it via VCS:

```bash
pip install git+https://your-host/vectra-client.git@main
```
