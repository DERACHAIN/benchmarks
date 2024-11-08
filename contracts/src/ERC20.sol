// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract BMToken is ERC20 {
  constructor(uint256 initialSupply) ERC20("BMToken", "BMT") {
    _mint(msg.sender, initialSupply);
  }
}