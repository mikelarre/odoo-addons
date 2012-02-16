# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2012 Avanzosc <http://www.avanzosc.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from osv import osv
from osv import fields
from tools.translate import _

class wiz_add_optional_fee(osv.osv_memory):
    _name = 'wiz.add.optional.fee'
    _description = 'Wizard to add optional fee'
 
    _columns = {
        'subject_list': fields.one2many('wiz.training.subject.master', 'wiz_id', 'List of Subjects'),
        'fee_list': fields.one2many('wiz.training.fee.master', 'wiz_id', 'List of Fee'),
        'recog_list': fields.one2many('wiz.training.recog.master', 'wiz_id', 'List of Recognition'),
    }
    
    def default_get(self, cr, uid, fields_list, context=None):
        values = {}
        ###########################
        # ARRAYS #
        ###########################
        fee_items = []
        recog_items = []
        seance_items = []
        ###########################
        # OBJETOS #
        ###########################
        product_obj = self.pool.get('product.product')
        sale_obj = self.pool.get('sale.order')
        job_obj = self.pool.get('res.partner.job')
        suscr_obj = self.pool.get('training.subscription.line')
        ###########################
        # FEE y RECOG #
        ###########################
        fee_ids = product_obj.search(cr, uid, [('training_charges', '=', 'fee')])
        recog_ids = product_obj.search(cr, uid, [('training_charges', '=', 'recog')])
        
        sale = sale_obj.browse(cr, uid, context['active_id'])
        
        job_id = job_obj.search(cr, uid, [('contact_id', '=', sale.contact_id.id)])
        suscription_id = suscr_obj.search(cr, uid, [('job_id', '=', job_id)])[0]
        suscription = suscr_obj.browse(cr, uid, suscription_id)
        
        for seance in suscription.session_id.seance_ids:
            seance_items.append({
                'name': seance.name,
                'product_id': seance.course_id.product_id.id,
                'date': seance.date,
                'duration': seance.duration,
                'state': seance.state,
                'wiz_id': 1,
            })
        for fee in product_obj.browse(cr, uid, fee_ids):
            fee_items.append({
                'name': fee.name,
                'product_id': fee.id,
                'wiz_id': 1,
            })
            
        for recog in product_obj.browse(cr, uid, recog_ids):
            recog_items.append({
                'name': recog.name,
                'product_id': recog.id,
                'wiz_id': 1,
            })
            
        values = {
            'fee_list': fee_items,
            'recog_list': recog_items,
            'subject_list': seance_items,
        }
        return values
    
    def insert_charge(self, cr, uid, ids, context=None):
        sale_line_obj = self.pool.get('sale.order.line')
        for wiz in self.browse(cr, uid, ids):
            for fee in wiz.fee_list:
                tax_list = []
                if fee.check:
                    values = {
                        'product_id': fee.product_id.id,
                        'name': fee.product_id.name,
                        'price_unit': fee.product_id.list_price,
                        'product_uom': fee.product_id.uom_id.id,
                        'order_id': context['active_id'],
                    }
                    for tax in fee.product_id.taxes_id:
                        tax_list.append(tax.id)
                    if tax_list:
                        values.update({
                            'tax_id': [(6, 0, tax_list)]
                        })
                    sale_line_obj.create(cr, uid, values)
            for recog in wiz.recog_list:
                tax_list = []
                if recog.check:
                    values = {
                        'product_id': recog.product_id.id,
                        'name': recog.product_id.name,
                        'price_unit': recog.product_id.list_price,
                        'product_uom': recog.product_id.uom_id.id,
                        'order_id': context['active_id'],
                    }
                    for tax in recog.product_id.taxes_id:
                        tax_list.append(tax.id)
                    if tax_list:
                        values.update({
                            'tax_id': [(6, 0, tax_list)]
                        })
                    sale_line_obj.create(cr, uid, values)
            for subject in wiz.subject_list:
                tax_list = []
                if subject.check:
                    if not subject.product_id:
                        raise osv.except_osv(_('Error!'),_('Subject does not have product assigned'))
                    values = {
                        'product_id': subject.product_id.id,
                        'name': subject.product_id.name,
                        'price_unit': subject.product_id.list_price,
                        'product_uom': subject.product_id.uom_id.id,
                        'order_id': context['active_id'],
                    }
                    for tax in subject.product_id.taxes_id:
                        tax_list.append(tax.id)
                    if tax_list:
                        values.update({
                            'tax_id': [(6, 0, tax_list)]
                        })
                    sale_line_obj.create(cr, uid, values)
        return {'type': 'ir.actions.act_window_close'}
    
wiz_add_optional_fee()

class wiz_training_subject_master(osv.osv_memory):
    _name = 'wiz.training.subject.master'
    _description = 'Subject Wizard List'
 
    _columns = {
        'name': fields.char('Name', size=64),
        'product_id': fields.many2one('product.product', 'Product', size=64),
        'date': fields.datetime('Date'),
        'duration': fields.float('Duration'),
        'state': fields.selection([
            ('opened','Opened'),
            ('confirmed','Confirmed'),
            ('inprogress','In Progress'),
            ('closed','Closed'),
            ('cancelled','Cancelled'),
            ('done','Done'),
        ], 'State'),
        'check': fields.boolean('Check'),
        'wiz_id': fields.many2one('wiz.add.optional.fee', 'Wizard'),
    }
wiz_training_subject_master()

class wiz_training_fee_master(osv.osv_memory):
    _name = 'wiz.training.fee.master'
    _description = 'Fee Wizard List'
 
    _columns = {
            'name': fields.char('Description', size=64),
            'product_id': fields.many2one('product.product', 'Product'),
            'check': fields.boolean('Check'),
            'wiz_id': fields.many2one('wiz.add.optional.fee', 'Wizard'),
        }
wiz_training_fee_master()

class wiz_training_recog_master(osv.osv_memory):
    _name = 'wiz.training.recog.master'
    _description = 'Recognition Wizard List'
 
    _columns = {
            'name': fields.char('Description', size=64),
            'product_id': fields.many2one('product.product', 'Product'),
            'check': fields.boolean('Check'),
            'wiz_id': fields.many2one('wiz.add.optional.fee', 'Wizard'),
        }
wiz_training_recog_master()

class wiz_training_record(osv.osv_memory):
    _name = 'wiz.training.record'
    _description = 'Record Wizard'
 
    _columns = {
            'record_ids': fields.many2many('training.record', 'record_ids_rel', 'wizard_id', 'record_id', 'Record', readonly=True),
    }
    
    def default_get(self, cr, uid, fields_list, context=None):
        values = {}
        record_obj = self.pool.get('training.record')
        for sale in self.pool.get('sale.order').browse(cr, uid, context['active_ids']):
            record_lst = record_obj.search(cr, uid, [('student_id', '=', sale.contact_id.id)])
            values = {
                'record_ids': record_lst,
            }
        return values
    
    def check_record(self, cr, uid, ids, context=None):
        print context
        return {}
wiz_training_record()