# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class AvaxContractDeployWizard(models.TransientModel):
    _name = 'avax.contract.deploy.wizard'
    _description = 'Avax Contract Deploy Wizard'

    @api.model
    def _get_default_contract_id(self):
        return self.env.context.get('active_id', False)

    account_id = fields.Many2one(
        'avax.account')

    balance = fields.Float(related='account_id.balance')
    password = fields.Char()
    contract_id = fields.Many2one(
        'avax.contract', default=_get_default_contract_id, required=True)
    connector_id = fields.Many2one(related='contract_id.connector_id')

    def action_deploy(self):
        for wizard in self:
            if wizard.password:
                wizard.contract_id._action_deploy(
                    wizard.account_id, wizard.password)
                return {'type': 'ir.actions.act_window_close'}
