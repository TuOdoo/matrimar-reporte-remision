
import calendar
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import base64
from datetime import date, datetime, time
import logging

import matplotlib.pyplot as plt
#import seaborn as sns
import io
import base64

_logger = logging.getLogger('[REPORTE REMISION]')

class ResPartnerRemision(models.Model):
    _name = 'res.partner.remision'
    _description = 'correo'

    parner_id = fields.Many2one(
        'res.partner', 'Nombre',
    )
    
    email = fields.Char(
        string="Correo",
        related="parner_id.email"
    )
    customer_id = fields.Many2one(
        'res.partner', 'Cliente',
    )

    company_id = fields.Many2one(
        'res.company', 'Compañia',
    )


    def cron_generar_reporte(self):
        #_logger.info('VAMOS BIEN 0')
        print("cron_generar_reporte 39")
        company = self._obtener_parametro_company()
        if company:
            for c in company:

                datos_para_reporte = self._generar_datos(c.id)
                print("docs", len(datos_para_reporte['form']['docs']))
                if len(datos_para_reporte['form']['docs']) > 0:
                    print("cron_generar_reporte 41",datos_para_reporte)

                    pdf = self.env.ref('matrimar_reporte_remision.action_report_reporte_remisiones_mult')._render_qweb_pdf(self.id, datos_para_reporte)

                    correos = self._obtener_parametro(c.id)

                    adjunto = self.action_get_attachment(pdf[0], name=f'Reporte remision.pdf')

                    html = "Reporte remision"
                    # _logger.info('VAMOS BIEN 10')

                    print("correos 60", correos , '; '.join(correos))
                    self._send_email(
                        adjunto=adjunto,
                        body=html,
                        email_to='; '.join(correos),
                        subject='Reporte remision test 1111'
                    )

    def _send_email(self, adjunto, body, email_to, subject):
        vals = {
            'subject': subject,
            'body_html': body,
            'email_to': email_to,
            # 'email_cc': '',
            'auto_delete': False,
            'email_from': 'noreply@matrimar.com',
            'attachment_ids': [(4, adjunto.id)]
        }

        mail_id = self.env['mail.mail'].create(vals)
        mail_id.sudo().send()

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

    def _obtener_parametro(self, company):
        print("xxxx     _values_conf    xxxxxx")
        domain = [
                ('company_id', '=', company),
            ]

        partner = self.env['res.partner.remision'].search(domain)
        email = []
        if partner:
            for c in partner:
                print("xxxxxx", c.parner_id, c.customer_id)
                email.append(c.parner_id.email)
        return email

    def _obtener_parametro_company(self):
        print("xxxx     _values_conf    xxxxxx")
        domain = [('id', '>=', 1)]
        company = self.env['res.company'].search(domain)

        return company

    def _corregir_desfase_horas(self):
        '''Solo obtiene el retraso de un día'''
        limite_inferior = datetime.strptime(str(fields.Date.today()), DATE_FORMAT) - timedelta(days=7)
        limite_superior = fecha = datetime.strptime(str(fields.Date.today()), DATE_FORMAT)

        return (limite_inferior, limite_superior)

    def _generar_datos(self, company):
        print("xxxxx    _generar_datos  xxxxxx")
        #self._values_conf()
        domain = [('company_id', '=', company)]
        partner = self.env['res.partner.remision'].search(domain)
        docs = []
        if partner:
            for c in partner:
                partners = self.env['res.partner'].search([('id', '=', c.customer_id.id)])
                if partners:
                    for p in partners.child_ids:
                        fecha_inicio, fecha_fin = self._corregir_desfase_horas()     
                        dominio_fechas = [('ticket_date', '>=', fecha_inicio),
                                        ('ticket_date', '<=', fecha_fin),
                                        ('partner_id', '=', p.id),
                                        ('company_id', '=', company)]

                        dominio = dominio_fechas

                        _logger.info('DOMINIO: %s', dominio)
                        pickings = self.env['stock.picking'].search(dominio)
                        for line in pickings:
                            docs.append(line)

        datos = {
            'wizard': 1,
            'form': {
                'docs': docs,

            }
        }
        print("xxx",datos)
        return datos

        