# AgniPariksha

## Dependencies to install:
```sh
> brew install locust

> python3 -m pip install --user pipenv

# For getting intellisense in vs code
> PIPENV_VENV_IN_PROJECT=1 pipenv shell

# Otherwise just run below command at root of the repo
> pipenv shell

# After inside virtual environment
> pipenv install
```

## Set env variables:
- Replace the variables in [local.env](./local.env) according to environment (for local they are already correctly set)
- Also make `IS_LOCAL` variable `false` for non-local environments.

# Running loadtest
```sh
> chmod +x run_customer.sh
> ./run_customer.sh

> chmod +x run_driver.sh
> ./run_driver.sh
```
