// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

contract Vault {
    mapping(address => uint256) public balances;

    function deposit() external payable { balances[msg.sender] += msg.value; }

    // Deliberate CTF fixture: state changes after the external call.
    function withdraw() external {
        uint256 amount = balances[msg.sender];
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok);
        balances[msg.sender] = 0;
    }
}
