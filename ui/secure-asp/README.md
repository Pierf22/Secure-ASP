<h1 align="center">The Secure ASP Website </h1>


## Table Of Contents

- [Requirements](#requirements)
- [Local development](#local-development)

## Requirements

- [Nodejs>=14.x](https://www.python.org/downloads/release/python-381/)
- [Angular](https://github.com/python-poetry/poetry)
- A SSL cert and key

> **NOTE** - Run all commands from the ui folder

## Local development
### Add your key and cert
To run the application with SSL encryption, you need to provide your own SSL key and certificate. These files should be placed in the ui/secure-asp/src/ssl-cert directory within the project structure.
### Installing Dependencies

To install the required dependencies, run the following command:
```shell
npm install
```
Running the Development Server

```shell
ng serve
``````

The Website will be available at [localhost:4200](http://localhost:4200)
