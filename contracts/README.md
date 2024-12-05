## Smart Contracts
This repo contrains ERC20 and ERC721 smart contracts for benchmarking.

### Build
```sh
$ forge build
```

### Deploy

- ERC20
```sh
$ forge create \
--rpc-url <rpc-url> \
--constructor-args <supply_number_in_wei> \
--private-key <private-key> \
src/ERC20.sol:BMToken
```

- ERC721
```sh
$ forge create \
--rpc-url <rpc-url> \
--constructor-args "BMFreemint" "BMNFT" \
--private-key <private-key> \
src/ERC721.sol:BMFreeMint
```

### Verify

- ERC20
```sh
$ forge verify-contract \
--rpc-url <rpc-url> \
--constructor-args $(cast abi-encode "constructor(uint256)" <supply_number_in_wei>) \
--verifier blockscout \
--verifier-url 'https://testnet.derachain.com/api/' \
<deployed-address> \
src/ERC20.sol:BMToken
```

- ERC721
```sh
$ forge verify-contract \
--rpc-url <rpc-url> \
--constructor-args $(cast abi-encode "constructor(string,string)" "BMFreemint" "BMNFT") \
--verifier blockscout \
--verifier-url 'https://testnet.derachain.com/api/' \
<deployed-address> \
src/ERC721.sol:BMFreeMint
```
*Note: please replace the endpoint of the explorer to `verifier-url` argument respectively with the testnet / mainnet*
