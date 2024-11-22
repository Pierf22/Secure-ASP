<h1 align="center">The Secure ASP API </h1>


## Table Of Contents

- [Requirements](#requirements)
- [Local development](#local-development)

## Requirements

- [Python >= 3.7](https://www.python.org/downloads/release/python-381/)
- [Poetry](https://github.com/python-poetry/poetry)
- A SSL cert and key 

> **NOTE** - Run all commands from the api folder

## Local development

### Add your key and cert
To run the application with SSL encryption, you need to provide your own SSL key and certificate. These files should be placed in the api/resources/ssl_cert directory within the project structure.
### Poetry

Create the virtual environment and install dependencies with:

```shell
poetry install
```

See the [poetry docs](https://python-poetry.org/docs/) for information on how to add/update dependencies.

Run commands inside the virtual environment with:

```shell
poetry run <your_command>
```

Spawn a shell inside the virtual environment with:

```shell
poetry shell
```

Start a development server locally:

```shell
 poetry run python -m app.main
```

API will be available at [localhost:8000/](http://localhost:8000/)

- Swagger UI docs at [localhost:8000/docs](http://localhost:8000/docs)
