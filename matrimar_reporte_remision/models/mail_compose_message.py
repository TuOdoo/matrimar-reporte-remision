
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import pytz
import logging
import io
import xlwt
import itertools
import base64
import logging
_logger = logging.getLogger('[ WIZARD SELECTOR FECHAS]')


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
    
    def generate_excel_report(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Reporte remision')
        style = xlwt.easyxf('font: bold True, name Arial;')
        bold = xlwt.easyxf("font: bold on;")
        worksheet.write(1, 1, str("Reporte remision"), bold)
        print_report_remision = ''
        for line in self.stock_picking_ids:
            print_report_remision = line.print_report_remision

        worksheet.write(2, 1, str(print_report_remision))
        worksheet.write(3, 0, 'Referencia', bold)
        worksheet.write(3, 1, 'Fecha ticket apex ', bold)
        worksheet.write(3, 2, 'Tiro', bold)
        worksheet.write(3, 3, 'Pedido', bold)
        worksheet.write(3, 4, 'Producto', bold)
        worksheet.write(3, 5, 'Cantidad', bold)
        row = 4
        ids = []
        totals = 0
        for line in self.stock_picking_ids:
            print("-------------------------------")
            worksheet.write(row, 0, line.name)
            worksheet.write(row, 1, line.ticket_date)
            worksheet.write(row, 2, line.partner_id.name)
            worksheet.write(row, 3, line.origin)
            worksheet.write(row, 4, line.product_id)
            worksheet.write(row, 5, line.qty_done_rr)
            row += 1
            totals += line.qty_done_rr
        row += 1
        worksheet.write(row, 4, "Cantidad")
        worksheet.write(row, 5, totals)
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        b64_excel = base64.b64encode(data)
        return self.env['ir.attachment'].create({
            'name': 'Reporte remision.xls',
            'type': 'binary',
            'datas': b64_excel,
            # 'datas_fname': name + '.pdf',
            'store_fname': 'Reporte remision.xls',
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.ms-excel'
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
            excel = self.generate_excel_report()
            self.attachment_ids += excel

    stock_picking_ids = fields.Many2many('stock.picking')

    notify_followers = fields.Boolean(default=True)

    def send_mail(self, auto_commit=False):
        for wizard in self:
            wizard = wizard.with_context(notify_followers=wizard.notify_followers)
            super(MailComposeMessage, wizard).send_mail(auto_commit=auto_commit)
        return True
