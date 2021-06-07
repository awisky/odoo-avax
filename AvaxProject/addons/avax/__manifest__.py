# © 2021 Agustin Wisky (<https://github.com/awisky>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Avax Blockchain Connector",
    "summary": "Avalanche Smart Contract",
    "version": "14.0.1.0.0",
    "category": "Localization",
    'author': "Agustin Wisky",
    'website': "https://github.com/awisky",
    "depends": [
        'contacts',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/avax_connector_views.xml',
        'wizard/avax_contract_wizard.xml',
        'views/avax_contract_views.xml',
        'views/avax_account_views.xml',
        'wizard/avax_connector_wizard.xml',
        'wizard/avax_account_wizard.xml',
        'wizard/avax_account_send_wizard.xml',
        'wizard/avax_contract_deploy_wizard.xml',
        'views/res_config_settings_views.xml',
        'views/menus_view.xml',
    ],
    'demo': [
        'demo/avax_demo.xml',
    ],
    "external_dependencies": {"python": ["web3", "solcx"]},
    'installable': True,
    'auto_install': False,
}
