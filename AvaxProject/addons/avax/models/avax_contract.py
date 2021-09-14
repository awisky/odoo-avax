# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from web3 import Web3
import json
import base64
from solcx import compile_standard

import logging

_logger = logging.getLogger(__name__)


class AvaxContractFunctionInput(models.Model):
    """
    Avax Contract Function Input
    """
    _name = 'avax.contract.function.input'
    _description = "Avax Contract Function"

    name = fields.Char()
    position = fields.Integer()
    function_id = fields.Many2one('avax.contract.function', required=True)
    input_type = fields.Char(required=True)


class AvaxContractFunction(models.Model):
    """
    Avax Contract Function
    """
    _name = 'avax.contract.function'
    _description = "Avax Contract Function"

    name = fields.Char(required=True)
    contract_id = fields.Many2one('avax.contract')
    state_mutability = fields.Selection(selection=[(
        'view', 'View'), ('payable', 'Payable'), ('nonpayable', 'Non Payable')])
    input_ids = fields.One2many(
        'avax.contract.function.input', 'function_id')


class AvaxContract(models.Model):
    """
    Avax Contract
    """
    _name = 'avax.contract'
    _description = "Avax Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        help='The name must be the same used in the smart contract definition')
    connector_id = fields.Many2one('avax.connector')
    account_id = fields.Many2one('avax.account')
    address = fields.Char()
    abi = fields.Text()
    solidity = fields.Text()
    bytecode = fields.Binary()
    explorer_url = fields.Char(compute='_compute_url')
    function_ids = fields.One2many(
        'avax.contract.function', 'contract_id', auto_join=True,
        compute='_compute_functions')

    @api.depends('name', 'connector_id')
    def name_get(self):
        result = []
        for rec in self:
            result.append((
                rec.id, _("%(name)s [%(connector)s]") % {
                    'name': rec.name, 'connector': rec.connector_id.name,
                })
            )
        return result

    @api.depends('abi')
    def _compute_functions(self):
        """
        This function is to construct the smart contract functions and inputs
        based on the abi json
        """
        avax_fun_obj = self.env['avax.contract.function']
        for rec in self:
            rec.function_ids = None
            if rec.abi:
                data = json.loads(rec.abi)
                for e in data:
                    if e['type'] == 'function':
                        inputs = []
                        for i, input in enumerate(e['inputs']):
                            inputs.append(
                                (0, 0, {'name': input['name'],
                                        'input_type': input['type'],
                                        'position': i}))
                        avax_func = avax_fun_obj.create(
                            {'name': e['name'],
                             'contract_id': rec.id,
                             'state_mutability': e['stateMutability'],
                             'input_ids': inputs})
                        rec.function_ids |= avax_func

    @api.depends('address', 'connector_id')
    def _compute_url(self):
        for rec in self:
            url = ''
            if rec.connector_id and rec.connector_id.explorer_url and \
                    rec.address:
                url = rec.connector_id.explorer_url+'address/'+rec.address
            rec.explorer_url = url

    def action_test(self):
        """
        Simple test to retrieve the functions from the smart contract
        """
        self.ensure_one()
        avax_provider = Web3.HTTPProvider(self.connector_id.service_url)
        w3 = Web3(avax_provider)
        contract = w3.eth.contract(address=self.address, abi=self.abi)
        msg = 'Contract Address:{}'.format(contract.address)+'\n'
        msg += 'Functions:\n'
        for fx in contract.all_functions():
            msg += '{}'.format(fx)+'\n'
        result = self._action_avax_connector_wizard(msg)
        return result

    def _action_avax_connector_wizard(self, message):
        """
        simple wizard call to show the messsage
        """
        action = self.env.ref('avax.avax_connector_wizard_form_action')
        result = action.sudo().read()[0]
        result['context'] = {'default_message': message}
        return result

    def action_compile(self):
        """
        """
        self.ensure_one()
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {
                self.name+".sol": {
                    "content": self.solidity
                }
            },
            "settings":
            {
                "outputSelection": {
                    "*": {
                        "*": [
                            "metadata", "evm.bytecode", "evm.bytecode.sourceMap"
                        ]
                    }
                }
            }
        })
        compiled_info = compiled_sol["contracts"][self.name+'.sol']
        key = list(compiled_info.keys())[0]
        root = compiled_info[key]
        bytecode = root["evm"]["bytecode"]["object"]
        abi = json.loads(root["metadata"])["output"]["abi"]
        self.abi = json.dumps(abi).encode("utf-8")
        self.bytecode = base64.b64encode(bytecode.encode("utf-8"))

    def _get_deploy_msg(self, args, response=None, tx_hash=None):
        msg = 'Deploy'
        if tx_hash:
            url = self.contract_id.connector_id.explorer_url+'tx/'+tx_hash.hex()
            msg += 'Transaction:{} \n'.format(tx_hash.hex())
            msg += 'Explorer:{} \n'.format(url)
        return msg

    def action_deploy(self):
        """
        """
        action = self.env.ref('avax.avax_contract_deploy_wizard_form_action')
        result = action.sudo().read()[0]
        return result

    def _action_deploy(self, account_id, password):
        """
        """
        self.ensure_one()
        avax_provider = Web3.HTTPProvider(self.connector_id.service_url)
        w3 = Web3(avax_provider)
        bytecode = base64.b64decode(self.bytecode).decode("utf-8")
        contract = w3.eth.contract(bytecode=bytecode, abi=self.abi)

        try:
            privatekey = w3.eth.account.decrypt(
                eval(account_id.encrypted_key), password)
        except Exception:
            raise ValidationError(_(
                "Wrong Password for {}".format(account_id.name)
            ))
            pass
        # Submit the transaction that deploys the contract

        nonce = w3.eth.getTransactionCount(account_id.address)

        withdraw_txn = contract.constructor().buildTransaction({
            'nonce': nonce,
            'chainId': self.connector_id.chain,
            'gasPrice': w3.eth.gas_price,
            'gas': 1000000
        })

        signed_tx = w3.eth.account.signTransaction(withdraw_txn, privatekey)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        addr = tx_receipt['contractAddress']
        self.address = addr
        url = self.connector_id.explorer_url+'tx/'+tx_hash.hex()
        msg = 'Transaction:{} \n'.format(tx_hash.hex())
        msg += 'Explorer:{} \n'.format(url)
        self.message_post(body=msg)
