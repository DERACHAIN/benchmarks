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
$ python main.py -a generate_wallets -n WALLET_NUMBER
```

- Fund wallets

```sh
$ python main.py -a bootstrap -t TOKEN_TYPE -b INITIAL_BALANCE
```

*Note: TOKEN_TYPE can be `native` or `erc20`*

- Transfer actions

```sh
$ python main.py -a transfer -n WALLET_NUMBER
```

## Run server

```sh
$ python main.py -a server --amount-native AMOUNT_NATIVE --amount-erc20 AMOUNT_ERC20
```

## PROD run

- Refer to [supervisord](./devops/README.md) for production config.

- It is necessary to increase the file descriptors number before running the benchmarks scripts
```sh
$ ulimit -n 8192
```
