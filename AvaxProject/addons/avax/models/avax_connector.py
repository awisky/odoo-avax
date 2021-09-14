# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from ast import literal_eval
from web3 import Web3

import logging

_logger = logging.getLogger(__name__)


class AvaxConnector(models.Model):
    """
    Avax Network connector

    Avalanche Mainnet Settings:
    Network Name: Avalanche Mainnet C-Chain
    New RPC URL: https://api.avax.network/ext/bc/C/rpc
    ChainID: 43114
    Symbol: AVAX
    Explorer: https://cchain.explorer.avax.network/

    FUJI Testnet Settings:
    Network Name: Avalanche FUJI C-Chain
    New RPC URL: https://api.avax-test.network/ext/bc/C/rpc
    ChainID: 43113
    Symbol: AVAX
    Explorer: https://cchain.explorer.avax-test.network

    Local Testnet (AVASH) Settings:
    Network Name: Avalanche Local
    New RPC URL: http://localhost:9650/ext/bc/C/rpc
    ChainID: 43112
    Symbol: AVAX
    Explorer: N/A
    """
    _name = 'avax.connector'
    _description = "Avax Network connector"

    name = fields.Char(required=True)
    service_url = fields.Char(required=True)
    chain = fields.Integer(required=True, string='Chain ID')
    symbol = fields.Char()
    explorer_url = fields.Char()
    fund_url = fields.Char()

    def _get_default_connector(self):
        """
        Returns the default configured Avax Connector
        """
        ICPSudo = self.env['ir.config_parameter'].sudo()
        connector_id = literal_eval(ICPSudo.get_param(
            'avax.avax_connector_id', default='False'
        ))
        avax_connector = None
        if connector_id:
            avax_connector = self.env['avax.connector'].browse(connector_id)
        return avax_connector

    def action_test(self):
        """
        Simple connection test
        """
        self.ensure_one()

        avax_provider = Web3.HTTPProvider(self.service_url)
        w3 = Web3(avax_provider)
        connected = w3.isConnected()
        result = self._action_avax_connector_wizard(
            'Connected to {}:{}'.format(self.name, connected))
        return result

    def _action_avax_connector_wizard(self, message):
        """
        simple wizard call to show the messsage
        """
        action = self.env.ref('avax.avax_connector_wizard_form_action')
        result = action.sudo().read()[0]
        result['context'] = {'default_message': message}
        return result
