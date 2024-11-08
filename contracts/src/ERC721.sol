// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract BMFreeMint is ERC721 {
  uint256 public nextTokenId;
  string private _baseTokenURI;

  constructor(string memory name, string memory symbol) ERC721(name, symbol) {
      nextTokenId = 0;
  }

  function mint() external {
      _safeMint(msg.sender, nextTokenId);
      nextTokenId++;
  }
}