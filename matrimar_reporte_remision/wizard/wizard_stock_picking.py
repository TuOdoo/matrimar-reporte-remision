# -*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo import models, fields, api
import pytz
import logging

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

    def _corregir_desfase_horas(self):
        '''Solo obtiene el retraso de un día'''


        _logger.info('FECHA INICIO: %s', self.fecha_inicio)

        limite_inferior = self.fecha_inicio 
        limite_superior = self.fecha_fin 

        return (limite_inferior, limite_superior)

    def generar_reporte(self):

        print("----------")


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

