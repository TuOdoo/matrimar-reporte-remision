
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

import base64
import logging


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def send_mail(self, auto_commit=False):
        if self.env.context.get('mark_so_as_sent') and self.model == 'stock.picking':
            self = self.with_context(mail_notify_author=self.env.user.partner_id in self.partner_ids)
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)

    def update_attachment(self):
        for rec in self:
            print("xxxx")
    
    def action_get_attachment(self, pdf, name):
        b64_pdf = base64.b64encode(pdf)
        return self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'datas': b64_pdf,
            # 'datas_fname': name + '.pdf',
            'store_fname': name,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    def datos_para_reporte(self):

        docs = []

        for line in self.stock_picking_ids:
            docs.append(line)

        datos = {
            'wizard': 1,
            'form': {
                'docs': docs,

            }
        }
        print("xxx",datos)
        return datos

    @api.onchange('partner_ids')
    def onchange_partner_ids(self):
        if self.stock_picking_ids:
            data = self.datos_para_reporte()
            pdf = self.env.ref('matrimar_reporte_remision.action_report_reporte_remisiones_mult')._render_qweb_pdf(self.id, data)

            adjunto = self.action_get_attachment(
                pdf[0], name='Reporte_logistica.pdf')
            self.attachment_ids = adjunto

    stock_picking_ids = fields.Many2many('stock.picking')

    notify_followers = fields.Boolean(default=True)

    def send_mail(self, auto_commit=False):
        for wizard in self:
            wizard = wizard.with_context(notify_followers=wizard.notify_followers)
            super(MailComposeMessage, wizard).send_mail(auto_commit=auto_commit)
        return True
