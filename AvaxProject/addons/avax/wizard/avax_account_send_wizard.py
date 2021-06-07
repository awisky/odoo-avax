# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class AvaxAccountSendWizard(models.TransientModel):
    _name = 'avax.account.send.wizard'
    _description = 'Avax Account SendWizard'

    @api.model
    def _get_default_account_id(self):
        return self.env.context.get('active_id', False)

    account_id = fields.Many2one(
        'avax.account', default=_get_default_account_id)

    balance = fields.Float(related='account_id.balance')
    password = fields.Char()
    account_to_id = fields.Many2one('avax.account')
    address = fields.Char(string='Destination Address')
    amount = fields.Integer()

    @api.onchange('account_to_id')
    def _onchange_(self):
        self.address = self.account_to_id and self.account_to_id.address or ''

    def action_send(self):
        for wizard in self:
            if wizard.password:
                account = self.env['avax.account'].browse(
                    self.env.context['active_id'])
                account._action_send(
                    password=wizard.password, to=wizard.address,
                    amount=wizard.amount)
                return {'type': 'ir.actions.act_window_close'}
