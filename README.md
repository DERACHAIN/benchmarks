# Benchmarks
The code benchmarking DERA chain, such as TPS, finality.

## Prerequisites

- [Python 3.11](https://www.python.org/downloads/release/python-3110/)

## Setup

- Install dependencies

```sh
$ pip install -r requirement.txt
```

## Smart contracts

- Please refer to [Smart Contracts](./contracts/README.md) for more details.

## Commands

- Generate wallets
```sh
$ python main.py -a generate_wallets
```

- Fund wallets
```sh
$ python main.py -a bootstrap -t <native | erc20> -b <initial_balance>
```

- Execute benchmarks
```sh
$ python main.py -a transfer -n <number_wallets> -tx <number_txs>
```

## PROD run
- It is necessary to increase the file descriptors number before running the benchmarks scripts
```sh
$ ulimit -n 8192
```
