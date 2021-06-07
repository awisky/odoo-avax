# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class AvaxAccountWizard(models.TransientModel):
    _name = 'avax.account.wizard'
    _description = 'Avax Account Wizard'

    password_1 = fields.Char()
    password_2 = fields.Char()

    def action_generate(self):
        for wizard in self:
            if wizard.password_1 and wizard.password_1 == wizard.password_2:
                account = self.env['avax.account'].browse(
                    self.env.context['active_id'])
                account._action_generate(wizard.password_1)
                return {'type': 'ir.actions.act_window_close'}
