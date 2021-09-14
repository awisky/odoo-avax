# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from web3 import Web3
import logging

_logger = logging.getLogger(__name__)


class AvaxAccount(models.Model):
    """
    Avax Account
    The connector is necessary because the account is created in a network
    """
    _name = 'avax.account'
    _description = "Avax Account"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    address = fields.Char()
    encrypted_key = fields.Text()
    balance = fields.Float()
    password = fields.Char()
    user_id = fields.Many2one('res.users')
    connector_id = fields.Many2one('avax.connector', required=True)
    explorer_url = fields.Char(compute='_compute_url')
    fund_url = fields.Char(related='connector_id.fund_url')

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

    @api.depends('address', 'connector_id')
    def _compute_url(self):
        for rec in self:
            url = ''
            if rec.connector_id and rec.connector_id.explorer_url and \
                    rec.address:
                url = rec.connector_id.explorer_url+'address/'+rec.address
            rec.explorer_url = url

    def _action_generate(self, password):
        """
        Creates an account with a passwork to encrypt the privatekey
        """
        self.ensure_one()
        avax_provider = Web3.HTTPProvider(self.connector_id.service_url)
        w3 = Web3(avax_provider)
        if self.name:
            account = w3.eth.account.create()
            self.address = Web3.toChecksumAddress(account.address)
            private_key = account.key
            _logger.info('=====PRIVATE KEY=======')
            _logger.info(private_key)
            _logger.info('=====PRIVATE KEY=======')
            keystore = account.encrypt(password)
            self.encrypted_key = keystore
        return

    def action_get_balance(self):
        """
        Gets the account balance
        """
        self.ensure_one()
        avax_provider = Web3.HTTPProvider(self.connector_id.service_url)
        w3 = Web3(avax_provider)
        if self.address:
            balance = w3.eth.getBalance(self.address)
            balance = w3.fromWei(balance, 'ether')
            self.balance = balance
        return

    def action_generate(self):
        """
        Account wizard creation
        """
        action = self.env.ref('avax.avax_account_wizard_form_action')
        result = action.sudo().read()[0]
        return result

    def action_send(self):
        """
        Send avax wizard
        """
        action = self.env.ref('avax.avax_account_send_wizard_form_action')
        result = action.sudo().read()[0]
        return result

    def _action_send(self, password, to, amount):
        """
        Function to send avax to another account
        """
        self.ensure_one()
        avax_provider = Web3.HTTPProvider(self.connector_id.service_url)
        w3 = Web3(avax_provider)

        nonce = w3.eth.get_transaction_count(self.address)

        account_to = Web3.toChecksumAddress(to)
        tx = {
            'nonce': nonce,
            'chainId': self.connector_id.chain,
            'gasPrice': w3.eth.gas_price,
            'gas': 100000,
            'to': account_to,
            'value': amount,
        }
        privatekey = w3.eth.account.decrypt(eval(self.encrypted_key), password)
        signed_tx = w3.eth.account.signTransaction(tx, privatekey)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        url = self.connector_id.explorer_url+'tx/'+tx_hash.hex()
        msg = 'Transaction:{} \n'.format(tx_hash.hex())
        msg += 'Explorer:{} \n'.format(url)
        self.message_post(body=msg)
        return

    def action_fund(self, password, to, amount):
        """
        got to fund
        """
