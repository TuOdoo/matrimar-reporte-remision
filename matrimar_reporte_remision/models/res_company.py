from odoo import fields, models, api
import logging
_logger = logging.getLogger('[CONFIG REPORTE REMISION]')

class ResCompany(models.Model):
    _inherit = 'res.company'

    res_partner_remision = fields.One2many(
        'res.partner.remision',
        'company_id',
        string='',
    )