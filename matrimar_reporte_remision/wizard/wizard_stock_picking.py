# -*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import models, fields, api
import pytz
import logging
import io
import xlwt
import itertools
from odoo.tools.misc import xlwt
import base64
_logger = logging.getLogger('[ WIZARD SELECTOR FECHAS]')


class WizardStockPicking(models.TransientModel):
    _name = 'wizard.stock.picking'
    _description = "Wizard stock picking"

    customer_id = fields.Many2one(
        'res.partner', 'Cliente',
    )
    partner_id = fields.Many2one(
        'res.partner', 'Tiro',
    )
    fecha_inicio = fields.Datetime(string='Fecha de inicio', required=True, default=fields.Datetime.now().replace(hour=0, minute=0, second=0)-timedelta(hours=18))
    fecha_fin = fields.Datetime(string='Fecha de fin', required=True, default=fields.Datetime.now(
    ).replace(hour=23, minute=59, second=59)-timedelta(hours=18))


    file_data = fields.Binary("File Data")

    def _corregir_desfase_horas(self):
        '''Solo obtiene el retraso de un día'''


        _logger.info('FECHA INICIO: %s', self.fecha_inicio)

        limite_inferior = self.fecha_inicio 
        limite_superior = self.fecha_fin 

        return (limite_inferior, limite_superior)

    def generar_reporte(self):

        print("----------")

        lang = self._context.get("lang")
        record_lang = self.env["res.lang"].search([("code", "=", lang)], limit=1)
        f1 = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.fecha_inicio)))[:10]
        format_date1 = datetime.strptime(f1, DEFAULT_SERVER_DATE_FORMAT).strftime(record_lang.date_format)
        f2 = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.fecha_fin)))[:10]
        format_date2 = datetime.strptime(f2, DEFAULT_SERVER_DATE_FORMAT).strftime(record_lang.date_format)
        ids = []
        if self.customer_id:
            partners = self.env['res.partner'].search([('id', '=', self.customer_id.id)])
            if partners:
                for p in partners.child_ids:
                    fecha_inicio, fecha_fin = self._corregir_desfase_horas()     
                    dominio_fechas = [('ticket_date', '>=', fecha_inicio),
                                    ('ticket_date', '<=', fecha_fin),
                                    ('partner_id', '=', p.id)]

                    dominio = dominio_fechas

                    _logger.info('DOMINIO: %s', dominio)
                    pickings = self.env['stock.picking'].search(dominio)
                    for line in pickings:
                        line.write({'print_report_remision': str("Del")+ str(" ")+ str(format_date1) + str(" ") + str("al") + str(" ") + str(format_date2)})
                        ids.append(line.id)
        else:
            fecha_inicio, fecha_fin = self._corregir_desfase_horas()     
            dominio_fechas = [('ticket_date', '>=', fecha_inicio),
                            ('ticket_date', '<=', fecha_fin),
                            ('partner_id', '=', self.partner_id.id)]

            dominio = dominio_fechas

            _logger.info('DOMINIO: %s', dominio)
            pickings = self.env['stock.picking'].search(dominio)
            for line in pickings:
                line.write({'print_report_remision': str("Del")+ str(" ")+ str(format_date1) + str(" ") + str("al") + str(" ") + str(format_date2)})
                ids.append(line.id)

        return {
            'name': "Traslados",
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ids)],
        }

    def cerrar(self):
        return {'type': 'ir.actions.act_window_close'}


    def generate_excel_report(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Reporte remision')
        style = xlwt.easyxf('font: bold True, name Arial;')

        lang = self._context.get("lang")
        record_lang = self.env["res.lang"].search([("code", "=", lang)], limit=1)
        f1 = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.fecha_inicio)))[:10]
        format_date1 = datetime.strptime(f1, DEFAULT_SERVER_DATE_FORMAT).strftime(record_lang.date_format)
        f2 = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.fecha_fin)))[:10]
        format_date2 = datetime.strptime(f2, DEFAULT_SERVER_DATE_FORMAT).strftime(record_lang.date_format)
        bold = xlwt.easyxf("font: bold on;")
        worksheet.write(1, 1, str("Reporte remision"), bold)
        worksheet.write(2, 1, str("Del")+ str(" ")+ str(format_date1) + str(" ") + str("al") + str(" ") + str(format_date2))

        worksheet.write(3, 0, 'Referencia', bold)
        worksheet.write(3, 1, 'Fecha ticket apex ', bold)
        worksheet.write(3, 2, 'Tiro', bold)
        worksheet.write(3, 3, 'Pedido', bold)
        worksheet.write(3, 4, 'Producto', bold)
        worksheet.write(3, 5, 'Cantidad', bold)
        row = 5
        ids = []
        totals = 0
        if self.customer_id:
            print("++++ 122 ++++++++")
            partners = self.env['res.partner'].search([('id', '=', self.customer_id.id)])
            print("+++++    124 +++++++",partners)
            if partners:
                for p in partners.child_ids:
                    fecha_inicio, fecha_fin = self._corregir_desfase_horas()     
                    dominio_fechas = [('ticket_date', '>=', fecha_inicio),
                                    ('ticket_date', '<=', fecha_fin),
                                    ('partner_id', '=', p.id)]

                    dominio = dominio_fechas

                    _logger.info('DOMINIO: %s', dominio)
                    pickings = self.env['stock.picking'].search(dominio)
                    print("-------------------------------", pickings)
                    for line in pickings:
                        print("-------------------------------")
                        worksheet.write(row, 0, line.name)
                        worksheet.write(row, 1, line.ticket_date)
                        worksheet.write(row, 2, line.partner_id.name)
                        worksheet.write(row, 3, line.origin)
                        worksheet.write(row, 4, line.product_id)
                        worksheet.write(row, 5, line.qty_done_rr)
                        row += 1
                        totals += line.qty_done_rr
        else:
            fecha_inicio, fecha_fin = self._corregir_desfase_horas()     
            dominio_fechas = [('ticket_date', '>=', fecha_inicio),
                            ('ticket_date', '<=', fecha_fin),
                            ('partner_id', '=', self.partner_id.id)]

            dominio = dominio_fechas

            _logger.info('DOMINIO: %s', dominio)
            pickings = self.env['stock.picking'].search(dominio)
            for line in pickings:
                print("-------------------------------")
                worksheet.write(row, 0, line.name)
                worksheet.write(row, 1, line.ticket_date)
                worksheet.write(row, 2, line.partner_id.name)
                worksheet.write(row, 3, line.origin)
                worksheet.write(row, 4, line.product_id.name)
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
        self.write({'file_data':base64.b64encode(data)})
        fp.close()
        action = {
            'name': 'Altas y Bajas',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model="+self._name+"&id=" + str(self.id) + "&field=file_data&download=true&filename=Reporte remision.xls",
            'target': 'self',
            }
        return action

