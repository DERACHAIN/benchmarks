# Supervisord
Keep long running process

## Dependencies

- Python 3.11 (by conda)

## Install dependencies

```sh
$ conda activate ENV_NAME
$ pip install supervisor
```

## Setup

- Create logs folder

```sh
$ mkdir /var/log/benchmarks
$ chown $(whoami):$(whoami) /var/log/benchmarks/
```

## Start

- Run following command from project folder

```sh
$ supervisord -c ./devops/supervisord.conf
```

## Manage

```sh
$ supervisorctl
```