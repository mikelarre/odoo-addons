# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class PurchaseRequisitionLineCreateOrder(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        requisition_obj = cls.env['purchase.requisition']
        product_obj = cls.env['product.product']
        supplier_obj = cls.env['res.partner']
        cls.supplier1 = supplier_obj.create({
            'name': 'supplier1',

        })
        cls.supplier2 = supplier_obj.create({
            'name': 'supplier2',

        })
        cls.product1 = product_obj.create({
            'name': 'Product1',
            'description_purchase': 'Purchase description',
            'variant_seller_ids': [(0, 0, {'name': cls.supplier1.id,
                                           'price': 5})]
        })
        cls.product2 = product_obj.create({
            'name': 'Product2',
            'variant_seller_ids': [(0, 0, {'name': cls.supplier2.id,
                                           'price': 7})]
        })
        cls.product3 = product_obj.create({
            'name': 'Product3',
        })
        cls.product4 = product_obj.create({
            'name': 'Product3',
        })
        cls.requisition = requisition_obj.create({
            'line_ids': [
                (0, 0, {'product_id': cls.product.id,
                        'product_qty': 2,
                        'schedule_date': '2020-01-13 00:00:00'
                })
            ]
        })
