# Contributing to AgenticADB

First off, thank you for considering contributing to AgenticADB! It's people like you that make open-source a great community.

## Local Setup

To set up your local development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/AgenticADB.git
   cd AgenticADB
   ```
2. Make sure you are using **Python 3.10+**.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install development dependencies (if not included in `requirements.txt`, such as `pytest` and `ruff`):
   ```bash
   pip install pytest ruff
   ```

## Testing Protocol

**Strict Rule:** Do not test against physical devices. All tests must pass using the mocked `pytest` suite.

Because we want to run tests efficiently across any CI/CD environment without needing hardware, all raw `adb` and `idb` subprocess commands are mocked in our test suite.

To run tests:
```bash
PYTHONPATH=AgenticADB python3 -m pytest -v AgenticADB/tests
```

Make sure that **all tests pass** before submitting a Pull Request.

## Branch Naming Conventions

Please create your branches based on the following pattern:
- For new features: `feature/<name-of-feature>`
- For bug fixes: `fix/<name-of-bug>`

## Commit Message Conventions

We strictly mandate the use of [Conventional Commits](https://www.conventionalcommits.org/). Your commit messages should be formatted as follows:

- `feat: <description>` - for new features
- `fix: <description>` - for bug fixes
- `docs: <description>` - for documentation changes
- `chore: <description>` - for maintenance tasks or tooling updates

Example: `feat: add support for fastmcp server`

## Pull Request Process

1. Ensure your branch is named correctly (`feature/...` or `fix/...`).
2. Verify that your commit messages follow Conventional Commits.
3. Make sure you've formatted the code using `ruff format .`.
4. Run the full test suite locally and ensure it passes using mocked testing (**Do not test against physical devices**).
5. Open a Pull Request on GitHub and describe the changes clearly.
6. A maintainer will review your code. You must pass all checks and the mocked `pytest` suite before your PR is merged.
