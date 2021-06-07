# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from ast import literal_eval
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    avax_connector_id = fields.Many2one('avax.connector')

    @api.model
    def get_values(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        avax_connector_id = literal_eval(ICPSudo.get_param(
            'avax.avax_connector_id',
            default='False'))
        res.update(
            avax_connector_id=avax_connector_id,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("avax.avax_connector_id",
                          self.avax_connector_id.id)
