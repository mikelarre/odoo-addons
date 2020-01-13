# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _
from itertools import groupby


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    supplier_id = fields.Many2one(comodel_name="res.partner",
                                  string="Supplier",
                                  domain="[('supplier', '=', True)]")
    description = fields.Text(string="Description")
    route_ids = fields.Many2many(related="product_id.route_ids",
                                 string="Routes")
    order_id = fields.Many2one(comodel_name="purchase.order")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        self.description = self.product_id.description_purchase
        self.supplier_id = self.product_id.variant_seller_ids.filtered(
            lambda x: x.product_id == self.product_id)[-1:].name
        self.supplier_id = self.product_id._select_seller(
            quantity=self.product_qty, date=self.schedule_date,
            uom_id=self.product_uom_id)
        self.price_unit = self.supplier_id.price
        return res

    def _prepare_order_lines(self, lines):
        prepared_lines = []
        for line in lines:
            prepared_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.name,
                'date_planned': line.schedule_date,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom_id.id,
                'price_unit': line.price_unit,
                'account_analytic_id': line.account_analytic_id.id
            }))
        return prepared_lines

    @api.multi
    def create_orders(self):
        purchase_obj = self.env['purchase.order']
        created_orders = self.env['purchase.order']
        requisition_lines = self.env['purchase.requisition.line']
        route_obj = self.env['stock.location.route']
        manufacture_route = route_obj.search([('name', '=', 'Manufacture')]).id
        allowed_lines = self.filtered(
            lambda x: not x.order_id and x.supplier_id and manufacture_route
            not in x.route_ids.ids)
        if not allowed_lines:
            raise exceptions.Warning(_("None of the lines meets the "
                                       "conditions: "
                                       "not order assigned, supplier "
                                       "assigned and 'Manufacture' not in "
                                       "routes"))
        for supplier, lines in groupby(allowed_lines, lambda x: x.supplier_id):
            for line in lines:
                requisition_lines |= line
            order = purchase_obj.create(
                {'partner_id': supplier.id,
                 'order_line': self._prepare_order_lines(requisition_lines), }
            )
            requisition_lines.write({'order_id': order.id})
            created_orders |= order
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchases',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': "[('id', 'in', {})]".format(created_orders.ids),
        }
