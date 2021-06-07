# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class AvaxConnectorWizard(models.TransientModel):
    _name = 'avax.connector.wizard'
    _description = 'Avax Connector Wizard'

    message = fields.Text(readonly=True)
