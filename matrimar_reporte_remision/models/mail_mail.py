from odoo import fields, models, api, _
from odoo.exceptions import UserError
from werkzeug.urls import url_encode

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, vals):
        print("+++++++++",self.recipient_ids)
        return super(MailMail, self).create(vals)