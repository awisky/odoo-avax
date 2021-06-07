### AVAX Odoo module to interact with accounts and smart contracts

A minimal odoo module to interact with the Avalanche blockchain.

### Goal

Hi Odooers, this is another minimal project that I wanted to share with you. My driver for this research was the smart contracts development and integration with Odoo. Of course, there are many alternatives to achieve this, but my scope was to find a blockchain compatible with the Ethereum virtual machine to run Solidity code faster and cheaper.

That's how I found AVAX.

### Avax

Avalanche ([AVAX](https://www.avax.network/)) is an Ethereum compatible 3rd generation blockchain.

Avax network site says: **Build without limits.** I think they are right.

I am amazed at how fast this network is. The transactions are executed in seconds, and the fees are notably lower than Ethereum.

Also, the documentation and support available are excellent.

I joined Avalanche Discord support to drop a few questions, and I received multiple responses in minutes.

Anyway, I could solve most of my work using what is available on the web.

### Odoo

So basically, I developed this basic Odoo module to interact with smart contracts in Avax.

The architecture of this module is oriented to test the Avax integration only. You may find a lot of improvement opportunities.

This Odoo module uses [Web3.py](https://web3py.readthedocs.io/en/stable/#). Web3.py is a python library for interacting with Ethereum, and it works perfectly with Avax too.

It has the Avax connector implementation, accounts, and smart contract functionality with certain limitations.

I included the FUJI Testnet connector set up in the demo data.

I packed this inside a docker-compose.

#### How to basic steps:

- Clone this repository
- Initialize the docker container
- Create a new odoo database
- Search and install the Avax module
- Create an Avax account from odoo
- Don't forget to fund your account with the faucet
- Create a smart contract, paste de solidity content in the solidity field
- Compile and deploy the smart contract
- Test the smart contract functionally. You need funds to write, to pay the gas of the transactions, but not for reading.

#### Notes:

This blog is research; please don't use this code in production.

I didn't want to use Metamask; I preferred to encrypt the key with a password entered by the user, so every time the user wants to sign a transaction, they will need to enter this password from Odoo instead of Metamask. If we store the password in Odoo, we can use the bot without human intervention.



I hope you like it :-)

