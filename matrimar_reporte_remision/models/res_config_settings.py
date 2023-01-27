from odoo import fields, models, api
import logging
_logger = logging.getLogger('[CONFIG REPORTE REMISION]')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    res_partner_remision = fields.Many2many(
        'res.partner.remision',
        related="company_id.res_partner_remision",
        readonly=False,
        string='',
    )
