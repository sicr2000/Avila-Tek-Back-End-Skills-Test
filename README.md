# Instructions

Use Dockers as Dev Container to run the database

## 1) Installation

> Important: This Back-End is made for python 3.10 but you can change the `python_version` on the Pipfile.

```sh
pipenv install;
pipenv run init;
pipenv run migrate;
pipenv run upgrade;
```

## 2) Migrations

## Remember to migrate every time you change your models

You have to migrate and upgrade the migrations for every update you make to your models:

```bash
$ pipenv run migrate # (to make the migrations)
$ pipenv run upgrade  # (to update your databse with the migrations)
```

## 3) Check your API live

1. Once you run the `pipenv run start` command your API will start running live and you can open it by clicking in the "ports" tab and then clicking "open browser".

## 4) API REST Documentation

You can open it using the url: 'http://localhost:3002/apidocs'

