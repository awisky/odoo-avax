# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from web3 import Web3


class AvaxContractWizardInput(models.TransientModel):
    _name = 'avax.contract.wizard.input'
    _description = 'Avax Contract Wizard Input'

    input_id = fields.Many2one('avax.contract.function.input', readonly=True)
    input_type = fields.Char(related='input_id.input_type')
    position = fields.Integer(related='input_id.position')
    value = fields.Char()
    account_id = fields.Many2one('avax.account')
    wizard_id = fields.Many2one('avax.contract.wizard')

    @api.onchange('account_id')
    def _onchange_(self):
        self.value = self.account_id and self.account_id.address or ''


class AvaxContractWizard(models.TransientModel):
    _name = 'avax.contract.wizard'
    _description = 'Avax Contract Wizard'

    account_id = fields.Many2one('avax.account')
    value = fields.Integer()
    password = fields.Char()
    function_id = fields.Many2one('avax.contract.function', readonly=True)
    contract_id = fields.Many2one(related='function_id.contract_id')

    state_mutability = fields.Selection(related='function_id.state_mutability')
    input_ids = fields.One2many(
        'avax.contract.wizard.input', 'wizard_id')

    @api.model
    def default_get(self, fields):
        res = super(AvaxContractWizard, self).default_get(fields)
        if self._context.get('function_id'):
            avax_func_obj = self.env['avax.contract.function']
            avax_func = avax_func_obj.browse(self._context.get('function_id'))
            inputs = []
            for input in avax_func.input_ids:
                inputs.append((0, 0, {'input_id': input.id}))
            res.update({
                'input_ids': inputs,
                'function_id': avax_func.id,
            })
        return res

    input_ids = fields.One2many('avax.contract.wizard.input', 'wizard_id')

    def action_test_function(self):
        """
        Simple test to retrieve the functions from the smart contract
        """
        self.ensure_one()
        avax_provider = Web3.HTTPProvider(
            self.contract_id.connector_id.service_url)
        w3 = Web3(avax_provider)
        contract = w3.eth.contract(
            address=self.contract_id.address, abi=self.contract_id.abi)
        if self.function_id.state_mutability == 'view':
            return self.action_test_view(contract)
        elif self.function_id.state_mutability == 'payable':
            return self.action_test_payable(contract, w3)
        elif self.function_id.state_mutability == 'nonpayable':
            return self.action_test_payable(contract, w3)

    def action_test_view(self, contract):
        """
        """
        self.ensure_one()

        args = self._get_args()
        response = contract.functions[self.function_id.name](*args).call()

        msg = self._get_msg(args, response)
        result = self.contract_id._action_avax_connector_wizard(msg)
        return result

    def _execute_transaction(self, w3, contract, args, account, password):

        try:
            privatekey = w3.eth.account.decrypt(
                eval(account.encrypted_key), password)
        except Exception:
            raise ValidationError(_(
                "Wrong Password for {}".format(account.name)
            ))
            pass
        if privatekey:
            nonce = w3.eth.get_transaction_count(account.address)
            txn_values = {
                'nonce': nonce,
                'chainId': self.contract_id.connector_id.chain,
                'gasPrice': w3.eth.gas_price,
                'gas': 1000000
            }
            if self.value:
                txn_values.update({'value': self.value})
            txn = contract.functions[self.function_id.name](
                *args).buildTransaction(txn_values)

            signed_tx = w3.eth.account.signTransaction(txn, privatekey)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            w3.eth.waitForTransactionReceipt(tx_hash)
        return tx_hash

    def _get_msg(self, args, response=None, tx_hash=None):
        msg = 'Function {}'.format(self.function_id.name)
        if args:
            for input in self.input_ids:
                msg += '{}:{}'.format(input.input_id.input_type,
                                      input.value)
        if response:
            msg += '\n Response: {}\n'.format(str(response))
        if tx_hash:
            url = self.contract_id.connector_id.explorer_url+'tx/'+tx_hash.hex()
            msg += 'Transaction:{} \n'.format(tx_hash.hex())
            msg += 'Explorer:{} \n'.format(url)
        return msg

    def _get_args(self):
        args = []
        for input in self.input_ids:
            val = input.value
            if input.input_id.input_type in 'uint256':
                val = int(input.value)
            args.append(val)
        return args

    def action_test_payable(self, contract, w3):
        """
        """
        self.ensure_one()
        args = self._get_args()
        tx_hash = self._execute_transaction(
            w3, contract, args, self.account_id, self.password)
        msg = self._get_msg(args, response=None, tx_hash=tx_hash)
        self.contract_id.message_post(body=msg)
        result = self.contract_id._action_avax_connector_wizard(msg)
        return result
