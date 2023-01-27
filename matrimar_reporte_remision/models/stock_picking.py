# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from werkzeug.urls import url_encode

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=True):
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        if share_token and hasattr(self, 'access_token'):
            params['access_token'] = self._portal_ensure_token()
        if pid:
            params['pid'] = pid
            params['hash'] = self._sign_token(pid)
        if signup_partner and hasattr(self, 'partner_id') and self.partner_id:
            params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

        return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))


    def _find_mail_template_picking(self, force_confirmation_template=False):
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('matrimar_reporte_remision.done_stock_picking', raise_if_not_found=False)

        return template_id

    def open_wizard(self):
        # return {
        #     'name': 'Wizard',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     "view_type": "form",
        #     'res_model': 'stock.picking.send',
        #     'target': 'new',
        #     'view_id': self.env.ref
        #     ('matrimar_reporte_remision.stock_picking_send_wizard_form').id,
        #     'context': {'active_id': self.id},
        # }

        model = self.env.context.get('active_model')
        lines = self.env[model].browse(
            self.env.context.get('active_ids', []))
        print("++++++", model, lines)
        ids = []
        if lines:
            for l in lines:
                ids.append(l.id)
        template_id = self._find_mail_template_picking()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        compose_form = self.env.ref('matrimar_reporte_remision.email_compose_message_wizard_form_remision', False)
        ctx = {
            'default_model': 'stock.picking',
            'active_id': self.ids,
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_stock_picking_ids': ids,
            'default_notify_followers': False,
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            #'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def _get_report_values(self, data=None):
        print("xxxxxxxxxx")
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(
            self.env.context.get('active_ids', []))
        return {
            'docs': docs,
        }
