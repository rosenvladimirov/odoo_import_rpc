import csv
import glob
import os
import sys

import odoorpc
import configparser
import logging
# import shutil
from bs4 import BeautifulSoup
# from setuptools.msvc import environ

logging.basicConfig()
_logger = logging.getLogger('odoorpc')
_logger.setLevel(logging.INFO)

CURRENT_ROW = os.environ.get('CURRENT_ROW', 0)
FIELD_ID_MAPPING_SAVE = {}
BLOCKED_FIELDS = []
ACTION = False
GLOBAL_SKIP = False
GLOBAL_MODE = 1  # 1 - normal, 2 - only link database
RPC_LANG = 'en_US'  # bg_BG, el_GR, en_US
STEPS = {'step_1': {}, 'step_2': {}, 'step_3': {}, 'step_4': {}, 'step_5': {}, 'step_6': {}, 'step_7': {}, 'step_8': {}, 'step_81': {},
         'step_9': {}, 'step_10': {}, 'step_11': {}, 'step_12': {}, 'step_13': {}, 'step_14': {}, 'step_15': {},
         'step_16': {}, 'step_17': {}, 'step_18': {}, 'step_181': {}, 'step_19': {}, 'step_191': {}, 'step_20': {},
         'step_21': {}, 'step_22': {}, 'step_23': {}, 'step_24': {}, 'step_25': {}, 'step_26': {}, 'step_27': {},
         'step_271': {}, 'step_272': {}, 'step_28': {}, 'step_29': {}, 'step_30': {}, 'step_31': {}, 'step_32': {},
         'step_33': {}, 'step_34': {}, 'step_35': {}, 'step_36': {}, 'step_37': {}, 'step_38': {}, 'step_39': {},
         'step_40': {}, 'step_41': {}, 'step_42': {}, 'step_43': {}, 'step_44': {}, 'step_45': {}}

EXECUTE_PROFILE = ''
EXECUTE_PROFILES = {
    'res.partner': '1,2',
    'product': '8, 9, 10',
    'product.update': '9, 10',
    'product.fix.attributes': '8, 81, 9, 10',
    'product.update.fix.attributes': '81, 9, 10',
    'sale.order': '19,20',
    'sale.order.additional.data.to.link': '191',
    'pricelist.items': '17, 18',
    'pricelis.product.set': '17, 181, 18',
    'purchase.order': '22, 23',
    'patient.data': '37,191',
    'product.supplierinfo.pricelist': '39,40',
    'product.supplierinfo': '40',
    'stock.picking': '33, 42, 43, 44',
}
EXECUTE = list(map(int, os.environ.get('EXECUTE', EXECUTE_PROFILES.get(EXECUTE_PROFILE, '1,2')).split(',')))

# [1] res.partner
STEPS['step_1']['MODEL'] = 'res.partner'  # Example model
STEPS['step_1']['TARGET_MODEL'] = ''
STEPS['step_1']['SEARCH_DOMAIN'] = [('is_company', '=', True), ('id', 'in', [10766, 1347,109,2768,2772,1273,4551,117,115,6626,10776,138,3366,191])]
# ('parent_id', '=', False)
STEPS['step_1']['SEARCH_DOMAINS'] = [[('product_manufacture_ids','!=',False), ('is_company','=',1), ('parent_id', '=', False)]]
STEPS['step_1']['FIELDS'] = ['name', 'email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
                             'country_id', 'country_id', 'street', 'street2',
                             'city', 'zip', 'phone', 'mobile', "image", "company_id", "image"]  # 'image', Example fields
STEPS['step_1']['SKIP_FIELDS'] = []
STEPS['step_1']['RELATIONAL_FIELDS'] = ['parent_id', 'country_id']  # Add other relational fields as needed
STEPS['step_1']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    # 'uid': 'l10n_bg_uic',
}
STEPS['step_1']['ORDER'] = 'id'
STEPS['step_1']['COMPARE_FILED'] = 'vat'
STEPS['step_1']['DEFAULT_FIELDS'] = {'company_id': 2}

# [2] persons in res.partner
STEPS['step_2']['MODEL'] = 'res.partner'  # Example model
STEPS['step_2']['TARGET_MODEL'] = ''
STEPS['step_2']['SEARCH_DOMAIN'] = []
STEPS['step_2']['SEARCH_DOMAINS'] = [[('parent_id', 'in', [10766, 1347,109,2768,2772,1273,4551,117,115,6626,10776,138,3366,191])]]
STEPS['step_2']['FIELDS'] = ['name', 'email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
                             'country_id', 'street', 'street2',
                             'city', 'zip', 'phone', 'mobile', "image"]
STEPS['step_2']['SKIP_FIELDS'] = []
STEPS['step_2']['RELATIONAL_FIELDS'] = ['parent_id', 'country_id']
STEPS['step_2']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    # 'uid': 'l10n_bg_uic',
}
STEPS['step_2']['ORDER'] = 'id'
STEPS['step_2']['COMPARE_FILED'] = 'ref'
STEPS['step_2']['DEFAULT_FIELDS'] = {'company_id': 2}

# [3] product.category
STEPS['step_3']['MODEL'] = 'product.category'  # Example model
STEPS['step_3']['TARGET_MODEL'] = ''
STEPS['step_3']['SEARCH_DOMAIN'] = [('id', '!=', 0)]
STEPS['step_3']['SEARCH_DOMAINS'] = [[('complete_name', 'like', 'All / Saleable%')]]
# STEPS['step_3']['SEARCH_DOMAINS'] = [[('complete_name', 'like', 'All')]]
STEPS['step_3']['FIELDS'] = ['name', 'parent_id', 'complete_name']
STEPS['step_3']['SKIP_FIELDS'] = []
STEPS['step_3']['RELATIONAL_FIELDS'] = ['parent_id']
STEPS['step_3']['FIELD_MAPPING'] = {}
STEPS['step_3']['ORDER'] = 'complete_name'
STEPS['step_3']['COMPARE_FILED'] = 'complete_name'

# [4] product attribute
STEPS['step_4']['MODEL'] = 'product.attribute'  # Example model
STEPS['step_4']['TARGET_MODEL'] = ''
STEPS['step_4']['SEARCH_DOMAIN'] = []
STEPS['step_4']['SEARCH_DOMAINS'] = [[('name', '!=', False)]]
STEPS['step_4']['FIELDS'] = ['name', 'parent_id', 'complete_name']
STEPS['step_4']['SKIP_FIELDS'] = []
STEPS['step_4']['RELATIONAL_FIELDS'] = []
STEPS['step_4']['FIELD_MAPPING'] = {}
STEPS['step_4']['ORDER'] = 'id'
STEPS['step_4']['COMPARE_FILED'] = ''

# [5] product.attribute.value
STEPS['step_5']['MODEL'] = 'product.attribute.value'
STEPS['step_5']['TARGET_MODEL'] = ''
STEPS['step_5']['SEARCH_DOMAIN'] = []
STEPS['step_5']['SEARCH_DOMAINS'] = [[('name', '!=', False)]]
STEPS['step_5']['FIELDS'] = ['name', 'sequence', 'attribute_id']
STEPS['step_5']['SKIP_FIELDS'] = []
STEPS['step_5']['RELATIONAL_FIELDS'] = ['attribute_id']
STEPS['step_5']['FIELD_MAPPING'] = {}
STEPS['step_5']['ORDER'] = 'id'
STEPS['step_5']['COMPARE_FILED'] = ''

# [6] product.uom.categ to uom.category
STEPS['step_6']['MODEL'] = 'product.uom.categ'
STEPS['step_6']['TARGET_MODEL'] = 'uom.category'
STEPS['step_6']['SEARCH_DOMAIN'] = []
STEPS['step_6']['SEARCH_DOMAINS'] = [[('name', '!=', False)]]
STEPS['step_6']['FIELDS'] = ['name']
STEPS['step_6']['SKIP_FIELDS'] = []
STEPS['step_6']['RELATIONAL_FIELDS'] = []
STEPS['step_6']['FIELD_MAPPING'] = {}
STEPS['step_6']['ORDER'] = 'id'
STEPS['step_6']['COMPARE_FILED'] = ''

# [7] product.uom to uom.uom
STEPS['step_7']['MODEL'] = 'product.uom'
STEPS['step_7']['TARGET_MODEL'] = 'uom.uom'
STEPS['step_7']['SEARCH_DOMAIN'] = []
STEPS['step_7']['SEARCH_DOMAINS'] = [[('active', '!=', False)]]
STEPS['step_7']['FIELDS'] = ['name', 'factor', 'uom_type', 'rounding']
STEPS['step_7']['SKIP_FIELDS'] = []
STEPS['step_7']['RELATIONAL_FIELDS'] = ['category_id']
STEPS['step_7']['FIELD_MAPPING'] = {}
STEPS['step_7']['ORDER'] = 'id'
STEPS['step_7']['COMPARE_FILED'] = ''

# [8] product.template
# [119117, 118591, 118591, 118912, 118628, 119106, 119121, 119131, 119129, 119130, 111583, 119108, 119132, 118999, 119127, 119125, 119122, 119133, 119136, 119123, 119124, 118628, 119106, 119121, 119131, 119129, 119130, 111583, 119108, 119132, 118999, 119127, 119125, 119122, 119133, 119136, 119123, 119124, 119100, 119111, 119137, 119112, 119126, 119113, 119092]
# ('id', 'in', [118377])
STEPS['step_8']['MODEL'] = 'product.template'
STEPS['step_8']['TARGET_MODEL'] = ''
STEPS['step_8']['SEARCH_DOMAIN'] = [('id', 'in', [119122, 119139, 119143, 119140, 119144])]
STEPS['step_8']['SEARCH_DOMAINS'] = [[('attribute_line_ids', '=', False)]]
# 'attribute_line_ids'
STEPS['step_8']['FIELDS'] = ['name', 'sequence', 'description', 'description_purchase', 'description_sale',
                             'tracking', 'taxes_id', 'supplier_taxes_id',
                             'type', 'standard_price', 'active',
                             'volume', 'weight', 'sale_ok', 'purchase_ok', 'active',
                             'default_code', 'categ_id', 'image', 'description']
STEPS['step_8']['SKIP_FIELDS'] = []
STEPS['step_8']['RELATIONAL_FIELDS'] = ['categ_id', 'taxes_id', 'supplier_taxes_id', 'attribute_line_ids', 'manufacturer_id']
STEPS['step_8']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    'specifications': 'alt_name',
}
STEPS['step_8']['FIELD_ID_MAPPING'] = {
    'taxes_id': [[42, 43, 21, 23, 25, 26, 27, 29], [164, 166, 1, 2, 4, 6, 7, 9]],
    'supplier_taxes_id': [[46, 49, 34, 154, 32, 143, 35], [151, 152, 12, 21, 16, 24, 13]],
}
STEPS['step_8']['ORDER'] = 'id'
STEPS['step_8']['COMPARE_FILED'] = 'default_code'
STEPS['step_8']['PRODUCT_CATEGORY'] = ['All']

# Denger not use this step without 9 and 10 steps
# ('id', 'in', [118377])
STEPS['step_81']['MODEL'] = 'product.template'
STEPS['step_81']['TARGET_MODEL'] = ''
STEPS['step_81']['ACTION'] = 'delete'
STEPS['step_81']['SEARCH_DOMAIN'] = [('id', '=', 119122)]
STEPS['step_81']['SEARCH_DOMAINS'] = [[('attribute_line_ids', '!=', False)]]
# 'attribute_line_ids'
STEPS['step_81']['FIELDS'] = ['attribute_line_ids', 'name']
STEPS['step_81']['SKIP_FIELDS'] = []
STEPS['step_81']['RELATIONAL_FIELDS'] = ['attribute_line_ids']
STEPS['step_81']['FIELD_MAPPING'] = {}
STEPS['step_81']['FIELD_ID_MAPPING'] = {}
STEPS['step_81']['ORDER'] = 'id'
STEPS['step_81']['COMPARE_FILED'] = 'default_code'
STEPS['step_81']['PRODUCT_CATEGORY'] = ['All']

# [9] product.attribute.line to product.template.attribute.line
# ('product_tmpl_id', 'in', [118377])
STEPS['step_9']['MODEL'] = 'product.attribute.line'
STEPS['step_9']['TARGET_MODEL'] = 'product.template.attribute.line'
STEPS['step_9']['SEARCH_DOMAIN'] = []
STEPS['step_9']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_9']['FIELDS'] = ['product_tmpl_id', 'attribute_id', 'value_ids']
STEPS['step_9']['SKIP_FIELDS'] = []
STEPS['step_9']['RELATIONAL_FIELDS'] = ['product_tmpl_id', 'attribute_id', 'value_ids']
STEPS['step_9']['FIELD_MAPPING'] = {}
STEPS['step_9']['ORDER'] = 'id'
STEPS['step_9']['COMPARE_FILED'] = ''

# [10] product.product
# ('attribute_value_ids', '!=', False)
# ('product_tmpl_id', 'in', [118377]) 65, 69, 76
# , ('id', '>', 1504), ('id', 'not in', [384, 386, 388, 390, 392, 945, 959, 961, 962, 967, 968, 1486, 1487, 1488, 1489, 1491, 1494, 1497, 1498, 1500, 1501, 1503, 1504])
STEPS['step_10']['MODEL'] = 'product.product'
STEPS['step_10']['TARGET_MODEL'] = ''
STEPS['step_10']['SEARCH_DOMAIN'] = [('product_tmpl_id', '=', [119122, 119139, 119143, 119140, 119144])]
STEPS['step_10']['SEARCH_DOMAINS'] = [[('attribute_value_ids', '=', False)]]
STEPS['step_10']['FIELDS'] = ['default_code', 'specifications', 'image', 'attribute_value_ids', 'product_tmpl_id']
STEPS['step_10']['SKIP_FIELDS'] = []
STEPS['step_10']['RELATIONAL_FIELDS'] = ['product_template_attribute_value_ids', 'product_tmpl_id']
STEPS['step_10']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    'specifications': 'alt_name',
    'attribute_value_ids': 'product_template_attribute_value_ids',
}
STEPS['step_10']['ORDER'] = 'id'
STEPS['step_10']['COMPARE_FILED'] = 'default_code'

# [11] product.attribute.value to product.template.attribute.value do not add for execution
STEPS['step_11']['MODEL'] = 'product.attribute.value'
STEPS['step_11']['TARGET_MODEL'] = 'product.template.attribute.value'
STEPS['step_11']['SEARCH_DOMAIN'] = []
STEPS['step_11']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_11']['FIELDS'] = ['name', 'attribute_id', 'price_extra', 'product_ids']
STEPS['step_11']['SKIP_FIELDS'] = []
STEPS['step_11']['RELATIONAL_FIELDS'] = ['attribute_id', 'product_ids']
STEPS['step_11']['FIELD_MAPPING'] = {}
STEPS['step_11']['ORDER'] = 'id'
STEPS['step_11']['COMPARE_FILED'] = ''

# [12] product.properties.static.dropdown
STEPS['step_12']['MODEL'] = 'product.properties.static.dropdown'
STEPS['step_12']['TARGET_MODEL'] = ''
STEPS['step_12']['SEARCH_DOMAIN'] = []
STEPS['step_12']['SEARCH_DOMAINS'] = [[('id', 'not in', [70, 71, 72, 75, 76, 85, 86, 88, 109, 110])]]
STEPS['step_12']['FIELDS'] = ['name', 'sequence', 'code', 'field_name']
STEPS['step_12']['SKIP_FIELDS'] = []
STEPS['step_12']['RELATIONAL_FIELDS'] = []
STEPS['step_12']['FIELD_MAPPING'] = {}
STEPS['step_12']['ORDER'] = 'id'
STEPS['step_12']['COMPARE_FILED'] = ''

# [13] product.properties.static - product.product
STEPS['step_13']['MODEL'] = 'product.properties.static'
STEPS['step_13']['TARGET_MODEL'] = ''
STEPS['step_13']['SEARCH_DOMAIN'] = [('object_id', '!=', False)]
STEPS['step_13']['SEARCH_DOMAINS'] = [[('object_id', 'ilike', 'product.product')]]
STEPS['step_13']['FIELDS'] = ['mdgp_class', 'mdgp_material', 'mdgp_category', 'mdgp_risk', 'mdgp_mri_allow',
                              'mdgp_mri_type',
                              'mdgp_steril_hosp', 'mdgp_steril_man', 'mdgp_useage', 'mdgp_service', 'mdgp_type',
                              'mdgp_anatomy',
                              'mdgp_device', 'mdgr_mil_spec', 'mdgr_future_c2', 'mdgr_future_c3', 'mdgr_alt_obs_code',
                              'mdgr_alt_obs_desc', 'mdgr_alt_obs_web', 'mdgr_alt_obs_price', 'mdbg_gmdn', 'mdbg_umdns',
                              'mdbg_bda_code', 'mdbg_bda_price', 'mdbg_rei_code', 'mdbg_rei_price',
                              'mdbg_future_code', 'mdcy_cda_code', 'mdcy_cda_price', 'mdcy_rei_code', 'mdcy_rei_price',
                              'mdcy_future_code', 'mdcy_gesy_desc', 'mdgr_eof_code', 'mdgr_eof_price',
                              'mdgr_observe_code',
                              'mdgr_observe_desc', 'mdgr_observe_price', 'mdgr_future_code', 'mdgr_ekapty_code',
                              'mdgr_observe_link', 'object_id',
                              ]
STEPS['step_13']['SKIP_FIELDS'] = []
STEPS['step_13']['RELATIONAL_FIELDS'] = ['object_id', 'mdgp_class', 'mdgp_category', 'mdgp_risk', 'mdgp_mri_allow',
                                         'mdgp_steril_hosp',
                                         'mdgp_steril_man', 'mdgp_useage', 'mdgp_service', 'mdgp_type', 'mdgp_anatomy',
                                         'mdgp_device', 'mdgr_mil_spec']
STEPS['step_13']['FIELD_MAPPING'] = {}
STEPS['step_13']['ORDER'] = 'id'
STEPS['step_13']['COMPARE_FILED'] = ''

# [14] product.properties.static - product.template
STEPS['step_14']['MODEL'] = 'product.properties.static'
STEPS['step_14']['TARGET_MODEL'] = ''
STEPS['step_14']['SEARCH_DOMAIN'] = [('object_id', '!=', False)]
STEPS['step_14']['SEARCH_DOMAINS'] = [[('object_id', 'ilike', 'product.template')]]
STEPS['step_14']['FIELDS'] = ['mdgp_class', 'mdgp_material', 'mdgp_category', 'mdgp_risk', 'mdgp_mri_allow',
                              'mdgp_mri_type',
                              'mdgp_steril_hosp', 'mdgp_steril_man', 'mdgp_useage', 'mdgp_service', 'mdgp_type',
                              'mdgp_anatomy',
                              'mdgp_device', 'mdgr_mil_spec', 'mdgr_future_c2', 'mdgr_future_c3', 'mdgr_alt_obs_code',
                              'mdgr_alt_obs_desc', 'mdgr_alt_obs_web', 'mdgr_alt_obs_price', 'mdbg_gmdn', 'mdbg_umdns',
                              'mdbg_bda_code', 'mdbg_bda_price', 'mdbg_rei_code', 'mdbg_rei_price',
                              'mdbg_future_code', 'mdcy_cda_code', 'mdcy_cda_price', 'mdcy_rei_code', 'mdcy_rei_price',
                              'mdcy_future_code', 'mdcy_gesy_desc', 'mdgr_eof_code', 'mdgr_eof_price',
                              'mdgr_observe_code',
                              'mdgr_observe_desc', 'mdgr_observe_price', 'mdgr_future_code', 'mdgr_ekapty_code',
                              'mdgr_observe_link', 'object_id',
                              ]
STEPS['step_14']['SKIP_FIELDS'] = []
STEPS['step_14']['RELATIONAL_FIELDS'] = ['object_id', 'mdgp_class', 'mdgp_category', 'mdgp_risk', 'mdgp_mri_allow',
                                         'mdgp_steril_hosp',
                                         'mdgp_steril_man', 'mdgp_useage', 'mdgp_service', 'mdgp_type', 'mdgp_anatomy',
                                         'mdgp_device', 'mdgr_mil_spec']
STEPS['step_14']['FIELD_MAPPING'] = {}
STEPS['step_14']['ORDER'] = 'id'
STEPS['step_14']['COMPARE_FILED'] = ''

# [15] 	product.set
STEPS['step_15']['MODEL'] = 'product.set'
STEPS['step_15']['TARGET_MODEL'] = ''
STEPS['step_15']['SEARCH_DOMAIN'] = []
STEPS['step_15']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_15']['FIELDS'] = ['name', 'code', 'image', 'partner_id', 'company_id']
STEPS['step_15']['SKIP_FIELDS'] = []
STEPS['step_15']['RELATIONAL_FIELDS'] = ['partner_id', 'company_id']
STEPS['step_15']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    'code': 'ref',
}
STEPS['step_15']['ORDER'] = 'id'
STEPS['step_15']['COMPARE_FILED'] = 'code'

# [25] 	product.set
STEPS['step_25']['MODEL'] = 'product.set'
STEPS['step_25']['TARGET_MODEL'] = ''
STEPS['step_25']['SEARCH_DOMAIN'] = []
STEPS['step_25']['SEARCH_DOMAINS'] = [[('id', '=', 120)]]
STEPS['step_25']['FIELDS'] = ['name', 'pricelist_id']
STEPS['step_25']['SKIP_FIELDS'] = []
STEPS['step_25']['RELATIONAL_FIELDS'] = [
    'pricelist_id'
]
STEPS['step_25']['FIELD_MAPPING'] = {
}
STEPS['step_25']['ORDER'] = 'id'
STEPS['step_25']['COMPARE_FILED'] = 'code'

# [16] 	product.set.line
STEPS['step_16']['MODEL'] = 'product.set.line'
STEPS['step_16']['TARGET_MODEL'] = ''
STEPS['step_16']['SEARCH_DOMAIN'] = [('product_tmpl_id', '!=', 114973)]
STEPS['step_16']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_16']['FIELDS'] = ['product_set_id', 'product_tmpl_id', 'quantity', 'sequence', 'company_id']
STEPS['step_16']['SKIP_FIELDS'] = []
STEPS['step_16']['RELATIONAL_FIELDS'] = ['product_id', 'product_set_id', 'product_tmpl_id', 'company_id']
STEPS['step_16']['FIELD_MAPPING'] = {
}
STEPS['step_16']['ORDER'] = 'id'
STEPS['step_16']['COMPARE_FILED'] = ''

# [17] 	product.pricelist
STEPS['step_17']['MODEL'] = 'product.pricelist'
STEPS['step_17']['TARGET_MODEL'] = ''
STEPS['step_17']['SEARCH_DOMAIN'] = [('company_id', '=', 6)]
STEPS['step_17']['SEARCH_DOMAINS'] = [[('active', '!=', False)]]
STEPS['step_17']['FIELDS'] = ['name', 'sequence', 'currency_id', 'company_id', 'discount_policy']
STEPS['step_17']['SKIP_FIELDS'] = []
STEPS['step_17']['RELATIONAL_FIELDS'] = ['currency_id', 'company_id']
STEPS['step_17']['FIELD_MAPPING'] = {
}
STEPS['step_17']['ORDER'] = 'id'
STEPS['step_17']['COMPARE_FILED'] = ''

# [18] 	product.pricelist.item
STEPS['step_18']['MODEL'] = 'product.pricelist.item'
STEPS['step_18']['TARGET_MODEL'] = ''
STEPS['step_18']['SEARCH_DOMAIN'] = []
STEPS['step_18']['SEARCH_DOMAINS'] = [[('company_id', '=', 6), ('active', '!=', False)]]
STEPS['step_18']['FIELDS'] = ['pricelist_id', 'company_id', 'currency_id', 'date_start', 'date_end', 'min_quantity',
                              'applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'base', 'compute_price',
                              'fixed_price', 'percent_price', 'price_discount', 'price_round', 'price_surcharge',
                              'price_min_margin', 'price_max_margin', 'product_set_id']
STEPS['step_18']['SKIP_FIELDS'] = []
STEPS['step_18']['RELATIONAL_FIELDS'] = ['pricelist_id',
                                         'company_id', 'currency_id', 'categ_id', 'product_tmpl_id',
                                         'product_id',
                                         'product_set_id']
STEPS['step_18']['FIELD_MAPPING'] = {
}
STEPS['step_18']['ORDER'] = 'id'
STEPS['step_18']['COMPARE_FILED'] = ''

# [181] product.pricelist.item for product.set
STEPS['step_181']['MODEL'] = 'product.pricelist.item'
STEPS['step_181']['TARGET_MODEL'] = 'product.set.pricelist'
STEPS['step_181']['SEARCH_DOMAIN'] = [('company_id', '=', 6), ('product_set_id', '!=', False), ('product_set_id', 'not in', [167, 150, 151])]
STEPS['step_181']['SEARCH_DOMAINS'] = [[('active', '!=', False)]]
STEPS['step_181']['FIELDS'] = ['pricelist_id', 'product_set_id']
STEPS['step_181']['SKIP_FIELDS'] = []
STEPS['step_181']['RELATIONAL_FIELDS'] = ['pricelist_id',
                                         'product_set_id']
STEPS['step_181']['FIELD_MAPPING'] = {
}
STEPS['step_181']['ORDER'] = 'id'
STEPS['step_181']['COMPARE_FILED'] = ''

# [19] 	sale.order
STEPS['step_19']['MODEL'] = 'sale.order'
STEPS['step_19']['TARGET_MODEL'] = 'sale.order'
STEPS['step_19']['SEARCH_DOMAIN'] = []
STEPS['step_19']['SEARCH_DOMAINS'] = [[('company_id', '=', 6)]]
STEPS['step_19']['FIELDS'] = ['name', 'date_order', 'partner_id', 'partner_contact_id', 'partner_invoice_id',
                              'partner_shipping_id', '', 'company_id', 'validity_date', 'create_date',
                              'currency_id', 'amount_untaxed', 'amount_tax', 'amount_total', 'patient_data_file_id',
                              'assistant_contact_ids']
STEPS['step_19']['SKIP_FIELDS'] = []
STEPS['step_19']['RELATIONAL_FIELDS'] = ['partner_id', 'partner_contact_id', 'partner_doctor_id', 'partner_invoice_id',
                                         'partner_shipping_id', 'currency_id', 'company_id', 'pricelist_id',
                                         'patient_data_file_id', 'assistant_contact_ids']
STEPS['step_19']['FIELD_MAPPING'] = {
    'partner_contact_id': 'partner_doctor_id',
}
STEPS['step_19']['ORDER'] = 'id'
STEPS['step_19']['COMPARE_FILED'] = ''

# [191] sale.order fast link
STEPS['step_191']['MODEL'] = 'sale.order'
STEPS['step_191']['TARGET_MODEL'] = 'sale.order'
STEPS['step_191']['SEARCH_DOMAIN'] = []
STEPS['step_191']['SEARCH_DOMAINS'] = [[('company_id', '=', 6)]]
STEPS['step_191']['FIELDS'] = ['patient_data_file_id',
                              'assistant_contact_ids']
STEPS['step_191']['SKIP_FIELDS'] = []
STEPS['step_191']['RELATIONAL_FIELDS'] = ['patient_data_file_id', 'assistant_contact_ids']
STEPS['step_191']['FIELD_MAPPING'] = {
}
STEPS['step_191']['ORDER'] = 'id'
STEPS['step_191']['COMPARE_FILED'] = ''

# [20] 	sale.order.line
# uom 79456, 52271
# ('order_id', 'not in', [16450, 16469, 16498, 16499])
STEPS['step_20']['MODEL'] = 'sale.order.line'
STEPS['step_20']['TARGET_MODEL'] = ''
STEPS['step_20']['SEARCH_DOMAIN'] = [('company_id', '=', 6), ('id', '>', 119666)]
STEPS['step_20']['SEARCH_DOMAINS'] = [[]]
# STEPS['step_20']['FIELDS'] = ['pricelist_id', 'company_id', 'currency_id', 'product_id', 'price_unit', 'product_uom',
#                               'product_uom_qty', 'product_set_id', 'discount', 'order_id']
STEPS['step_20']['FIELDS'] = ['price_unit', 'order_id', 'product_id']
STEPS['step_20']['SKIP_FIELDS'] = []
STEPS['step_20']['RELATIONAL_FIELDS'] = ['pricelist_id', 'company_id', 'currency_id', 'categ_id', 'product_tmpl_id',
                                         'product_id', 'order_id', 'product_uom',
                                         'product_set_id']
STEPS['step_20']['FIELD_MAPPING'] = {
}
STEPS['step_8']['FIELD_ID_MAPPING'] = {
    'product_id': [78879, 1793],
}
STEPS['step_20']['ORDER'] = 'id'
STEPS['step_20']['COMPARE_FILED'] = ''

# [22] 	purchase.order
STEPS['step_22']['MODEL'] = 'purchase.order'
STEPS['step_22']['TARGET_MODEL'] = ''
STEPS['step_22']['SEARCH_DOMAIN'] = []
STEPS['step_22']['SEARCH_DOMAINS'] = [[('company_id', '=', 6)]]
STEPS['step_22']['FIELDS'] = ['name', 'origin', 'partner_ref', 'date_order', 'date_approve', 'partner_id', 'dest_address_id',
                              'company_id', 'picking_type_id', 'picking_type_id',
                              'currency_id']
STEPS['step_22']['CHILD_FIELDS'] = []
STEPS['step_22']['SKIP_FIELDS'] = []
STEPS['step_22']['RELATIONAL_FIELDS'] = ['partner_id', 'dest_address_id', 'currency_id', 'fiscal_position_id', 'company_id']
STEPS['step_22']['FIELD_MAPPING'] = {

}
STEPS['step_22']['FIELD_ID_MAPPING'] = {
    # 'fiscal_position_id': [[31, 32, 33], [10, 11, 12]],
}
STEPS['step_22']['ORDER'] = 'id'
STEPS['step_22']['COMPARE_FILED'] = ''

# [23] 	purchase.order.line
STEPS['step_23']['MODEL'] = 'purchase.order.line'
STEPS['step_23']['TARGET_MODEL'] = ''
STEPS['step_23']['SEARCH_DOMAIN'] = [('order_id.sets_line', '=', False)]
STEPS['step_23']['SEARCH_DOMAINS'] = [[('order_id.company_id', '=', 6), ('order_id', 'in', [1313, 1196, 2042, 2918])]]
STEPS['step_23']['FIELDS'] = ['company_id', 'currency_id', 'categ_id',
                              'product_id', 'order_id', 'product_uom',
                              'product_set_id', 'product_qty', 'price_unit']
STEPS['step_23']['CHILD_FIELDS'] = []
STEPS['step_23']['SKIP_FIELDS'] = []
STEPS['step_23']['RELATIONAL_FIELDS'] = ['company_id', 'currency_id', 'categ_id', 'product_tmpl_id',
                                         'product_id', 'order_id', 'product_uom', 'taxes_id', 'price_unit',
                                         'product_set_id']
STEPS['step_23']['FIELD_MAPPING'] = {

}
STEPS['step_23']['FIELD_ID_MAPPING'] = {
    'taxes_id': [[46, 49, 34, 154, 32, 143, 35], [151, 152, 12, 21, 16, 24, 13]],
    # 'fiscal_position_id': [[31, 32, 33], [10, 11, 12]],
}
STEPS['step_23']['ORDER'] = 'id'
STEPS['step_23']['COMPARE_FILED'] = ''

# [24] 	product.manufacturer
STEPS['step_24']['MODEL'] = 'product.manufacturer'
STEPS['step_24']['TARGET_MODEL'] = ''
STEPS['step_24']['SEARCH_DOMAIN'] = [('id', '!=', 0)]
STEPS['step_24']['SEARCH_DOMAINS'] = [[('active', '=', True), ('manufacturer', '!=', False)]]
STEPS['step_24']['FIELDS'] = ['sequence', 'manufacturer_pname', 'manufacturer_pref',
                              'manufacturer_purl', 'manufacturer',
                              'product_tmpl_id']
STEPS['step_24']['CHILD_FIELDS'] = []
STEPS['step_24']['SKIP_FIELDS'] = []
STEPS['step_24']['RELATIONAL_FIELDS'] = ['product_tmpl_id', 'product_id', 'manufacturer']
STEPS['step_24']['FIELD_MAPPING'] = {
}
STEPS['step_24']['ORDER'] = 'id'
STEPS['step_24']['COMPARE_FILED'] = ''

# [25] 	product.manufacturer.datasheets
STEPS['step_25']['MODEL'] = 'product.manufacturer.datasheets'
STEPS['step_25']['TARGET_MODEL'] = ''
STEPS['step_25']['SEARCH_DOMAIN'] = [('manufacturer_id', '!=', 143)]
STEPS['step_25']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_25']['FIELDS'] = ['datas_fname', 'name', 'version', 'manufacturer_id', 'res_model', 'res_id', 'res_name',
                              'store_fname', 'description', 'type', 'mimetype']
STEPS['step_25']['CHILD_FIELDS'] = []
STEPS['step_25']['SKIP_FIELDS'] = []
STEPS['step_25']['RELATIONAL_FIELDS'] = ['manufacturer_id']
STEPS['step_25']['FIELD_MAPPING'] = {
}
STEPS['step_25']['ORDER'] = 'id'
STEPS['step_25']['COMPARE_FILED'] = ''

STEPS['step_271']['MODEL'] = 'product.packaging.type'
STEPS['step_271']['TARGET_MODEL'] = ''
STEPS['step_271']['SEARCH_DOMAIN'] = []
STEPS['step_271']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_271']['FIELDS'] = ['categ_id', 'product_tmpl_id', 'product_id', 'product_manufacturer_id', 'name', 'code',
                              'volume_type', 'qty']
STEPS['step_271']['CHILD_FIELDS'] = []
STEPS['step_271']['SKIP_FIELDS'] = []
STEPS['step_271']['RELATIONAL_FIELDS'] = ['categ_id', 'product_tmpl_id', 'product_manufacturer_id', 'product_id']
STEPS['step_271']['FIELD_MAPPING'] = {
}
STEPS['step_271']['ORDER'] = 'id'
STEPS['step_271']['COMPARE_FILED'] = ''

STEPS['step_26']['MODEL'] = 'product.category.packaging.type'
STEPS['step_26']['TARGET_MODEL'] = 'product.packaging.category.type'
STEPS['step_26']['SEARCH_DOMAIN'] = []
STEPS['step_26']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_26']['FIELDS'] = ['name', 'code', 'volume_type']
STEPS['step_26']['CHILD_FIELDS'] = []
STEPS['step_26']['SKIP_FIELDS'] = []
STEPS['step_26']['RELATIONAL_FIELDS'] = []
STEPS['step_26']['FIELD_MAPPING'] = {
}
STEPS['step_26']['ORDER'] = 'id'
STEPS['step_26']['COMPARE_FILED'] = ''

STEPS['step_272']['MODEL'] = 'product.packaging.type'
STEPS['step_272']['TARGET_MODEL'] = 'product.packaging.reel'
STEPS['step_272']['SEARCH_DOMAIN'] = []
STEPS['step_272']['SEARCH_DOMAINS'] = [[('id', '!=', False), ('product_manufacturer_id', '!=', False), ('product_tmpl_id', '!=', False)]]
STEPS['step_272']['FIELDS'] = ['product_tmpl_id', 'product_manufacturer_id', 'code', 'volume_type', 'qty']
STEPS['step_272']['CHILD_FIELDS'] = []
STEPS['step_272']['SKIP_FIELDS'] = []
STEPS['step_272']['RELATIONAL_FIELDS'] = ['product_tmpl_id', 'manufacturer_id', 'product_id']
STEPS['step_272']['FIELD_MAPPING'] = {
    'product_manufacturer_id': 'manufacturer_id',
    'code': 'name',
}
STEPS['step_272']['ORDER'] = 'id'
STEPS['step_272']['COMPARE_FILED'] = ''

STEPS['step_27']['MODEL'] = 'mrp.bom'
STEPS['step_27']['TARGET_MODEL'] = ''
STEPS['step_27']['SEARCH_DOMAIN'] = []
STEPS['step_27']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_27']['FIELDS'] = ['code', 'type', 'product_tmpl_id', 'product_id', 'product_qty', 'product_uom_id',
                              'sequence', 'company_id']
STEPS['step_27']['CHILD_FIELDS'] = []
STEPS['step_27']['SKIP_FIELDS'] = []
STEPS['step_27']['RELATIONAL_FIELDS'] = ['product_tmpl_id', 'product_id', 'product_uom_id', 'company_id']
STEPS['step_27']['FIELD_MAPPING'] = {
}
STEPS['step_27']['ORDER'] = 'id'
STEPS['step_27']['COMPARE_FILED'] = ''

STEPS['step_28']['MODEL'] = 'mrp.bom.line'
STEPS['step_28']['TARGET_MODEL'] = ''
STEPS['step_28']['SEARCH_DOMAIN'] = []
STEPS['step_28']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_28']['FIELDS'] = ['product_id', 'product_qty', 'product_uom_id', 'sequence', 'bom_id',
                              'attribute_value_ids', 'sequence']
STEPS['step_28']['CHILD_FIELDS'] = []
STEPS['step_28']['SKIP_FIELDS'] = []
STEPS['step_28']['RELATIONAL_FIELDS'] = ['bom_id', 'product_id', 'product_uom_id']
STEPS['step_28']['FIELD_MAPPING'] = {
}
STEPS['step_28']['ORDER'] = 'id'
STEPS['step_28']['COMPARE_FILED'] = ''

STEPS['step_29']['MODEL'] = 'mrp.routing'
STEPS['step_29']['TARGET_MODEL'] = ''
STEPS['step_29']['SEARCH_DOMAIN'] = []
STEPS['step_29']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_29']['FIELDS'] = ['name', 'code', 'note', 'company_id']
STEPS['step_29']['CHILD_FIELDS'] = []
STEPS['step_29']['SKIP_FIELDS'] = []
STEPS['step_29']['RELATIONAL_FIELDS'] = ['company_id']
STEPS['step_29']['FIELD_MAPPING'] = {
}
STEPS['step_29']['ORDER'] = 'id'
STEPS['step_29']['COMPARE_FILED'] = ''

STEPS['step_30']['MODEL'] = 'mrp.routing.workcenter'
STEPS['step_30']['TARGET_MODEL'] = ''
STEPS['step_30']['SEARCH_DOMAIN'] = []
STEPS['step_30']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_30']['FIELDS'] = ['name', 'sequence', 'routing_id', 'note', 'time_mode_batch', 'time_cycle_manual',
                              'time_cycle', 'workorder_count', 'batch', 'batch_size', 'company_id']
STEPS['step_31']['CHILD_FIELDS'] = []
STEPS['step_31']['SKIP_FIELDS'] = []
STEPS['step_31']['RELATIONAL_FIELDS'] = ['routing_id', 'company_id']
STEPS['step_31']['FIELD_MAPPING'] = {
}
STEPS['step_31']['ORDER'] = 'id'
STEPS['step_31']['COMPARE_FILED'] = ''

STEPS['step_31']['MODEL'] = 'mrp.workcenter'
STEPS['step_31']['TARGET_MODEL'] = ''
STEPS['step_31']['SEARCH_DOMAIN'] = []
STEPS['step_31']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_31']['FIELDS'] = ['name', 'time_efficiency', 'note', 'capacity', 'sequence', 'color',
                              'time_start', 'time_stop', 'batch', 'batch_size', 'company_id']
STEPS['step_31']['CHILD_FIELDS'] = []
STEPS['step_31']['SKIP_FIELDS'] = []
STEPS['step_31']['RELATIONAL_FIELDS'] = ['routing_id', 'company_id']
STEPS['step_31']['FIELD_MAPPING'] = {
}
STEPS['step_31']['ORDER'] = 'id'
STEPS['step_31']['COMPARE_FILED'] = ''

STEPS['step_32']['MODEL'] = 'stock.quant'
STEPS['step_32']['TARGET_MODEL'] = ''
STEPS['step_32']['SEARCH_DOMAIN'] = [('location_id', 'in', [163]), ('product_id.type', '!=', 'service')]
STEPS['step_32']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_32']['FIELDS'] = ['product_id', 'location_id', 'company_id', 'lot_id', 'quantity']
STEPS['step_32']['CHILD_FIELDS'] = []
STEPS['step_32']['SKIP_FIELDS'] = []
STEPS['step_32']['RELATIONAL_FIELDS'] = ['product_id', 'location_id', 'company_id', 'lot_id']
STEPS['step_32']['FIELD_MAPPING'] = {
}
STEPS['step_32']['ORDER'] = 'id'
STEPS['step_32']['COMPARE_FILED'] = ''

STEPS['step_33']['MODEL'] = 'stock.production.lot'
STEPS['step_33']['TARGET_MODEL'] = 'stock.lot'
STEPS['step_33']['SEARCH_DOMAIN'] = []
STEPS['step_33']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_33']['FIELDS'] = ['name', 'ref', 'product_id', 'create_date', 'company_id']
STEPS['step_33']['CHILD_FIELDS'] = []
STEPS['step_33']['SKIP_FIELDS'] = []
STEPS['step_33']['RELATIONAL_FIELDS'] = ['product_id', 'company_id']
STEPS['step_33']['FIELD_MAPPING'] = {
}
STEPS['step_33']['ORDER'] = 'id'
STEPS['step_33']['COMPARE_FILED'] = ''

STEPS['step_34']['MODEL'] = 'hr.rfid.card'
STEPS['step_34']['TARGET_MODEL'] = 'hr.rfid.card'
STEPS['step_34']['SEARCH_DOMAIN'] = []
STEPS['step_34']['SEARCH_DOMAINS'] = [[('id', '!=', False), ('contact_id', '=', False)]]
STEPS['step_34']['FIELDS'] = ['name', 'internal_number', 'number', 'card_input_type', 'card_reference',
                              'employee_id', 'contact_id', 'activate_on', 'deactivate_on', 'active', 'cloud_card']
STEPS['step_34']['CHILD_FIELDS'] = []
STEPS['step_34']['SKIP_FIELDS'] = []
STEPS['step_34']['RELATIONAL_FIELDS'] = ['employee_id', 'contact_id']
STEPS['step_34']['FIELD_MAPPING'] = {
}
STEPS['step_34']['ORDER'] = 'id'
STEPS['step_34']['COMPARE_FILED'] = ''

# res.users
STEPS['step_35']['MODEL'] = 'res.users'
STEPS['step_35']['TARGET_MODEL'] = 'res.users'
STEPS['step_35']['SEARCH_DOMAIN'] = [('id', 'not in', [251, 2])]
STEPS['step_35']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_35']['FIELDS'] = ['login', 'signature', 'tz_offset', 'name', 'email']
STEPS['step_35']['CHILD_FIELDS'] = []
STEPS['step_35']['SKIP_FIELDS'] = []
STEPS['step_35']['RELATIONAL_FIELDS'] = ['partner_id']
STEPS['step_35']['FIELD_MAPPING'] = {
}
STEPS['step_35']['ORDER'] = 'id'
STEPS['step_35']['COMPARE_FILED'] = 'ref'

# hr.employee
STEPS['step_36']['MODEL'] = 'hr.employee'
STEPS['step_36']['TARGET_MODEL'] = 'hr.employee'
STEPS['step_36']['SEARCH_DOMAIN'] = []
STEPS['step_36']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_36']['FIELDS'] = ['name', 'active', 'image_128', 'avatar_256', 'avatar_512', 'avatar_1024', 'image_1920']
STEPS['step_36']['CHILD_FIELDS'] = []
STEPS['step_36']['SKIP_FIELDS'] = []
STEPS['step_36']['RELATIONAL_FIELDS'] = []
STEPS['step_36']['FIELD_MAPPING'] = {
}
STEPS['step_36']['ORDER'] = 'id'
STEPS['step_36']['COMPARE_FILED'] = ''

# patient.data
STEPS['step_37']['MODEL'] = 'patient.data'
STEPS['step_37']['TARGET_MODEL'] = ''
STEPS['step_37']['SEARCH_DOMAIN'] = [('company_id', '=', 6), ("order_ids", "!=", False), ('id', '>=', 55452)]
STEPS['step_37']['SEARCH_DOMAINS'] = [[]]
STEPS['step_37']['FIELDS'] = ['name', 'partner_patient_id', 'partner_id',
                              'patient_clinical_path_ref', 'patient_incident_nr', 'patient_visit_nr',
                              'patient_clinical_case_number',  'patient_name',
                              'patient_date_of_birth', 'patient_material_aquisition', 'patient_fund_confirmation', 'patient_ada',
                              'patient_tender', 'patient_surgery_date', 'isupply_contract', 'isupply_contract_date',
                              'isupply_order_number', 'isupply_order_date', 'fund_verification', 'patient_case_pics',
                              'company_id', 'order_ids']
STEPS['step_37']['CHILD_FIELDS'] = []
STEPS['step_37']['SKIP_FIELDS'] = []
STEPS['step_37']['RELATIONAL_FIELDS'] = ['partner_patient_id', 'partner_id', 'hospital_partner_id', 'patient_partner_id', 'company_id', 'order_ids']
STEPS['step_37']['FIELD_MAPPING'] = {
    'partner_id': 'hospital_partner_id',
    'partner_patient_id': 'patient_partner_id',
    'patient_date_of_birth': 'birthdate_date',
    'patient_material_aquisition': 'patient_material_acquisition',
}
STEPS['step_37']['ORDER'] = 'id'
STEPS['step_37']['COMPARE_FILED'] = ''

# stock.location
STEPS['step_38']['MODEL'] = 'stock.location'
STEPS['step_38']['TARGET_MODEL'] = ''
STEPS['step_38']['SEARCH_DOMAIN'] = []
STEPS['step_38']['SEARCH_DOMAINS'] = [[('location_id', '=', 8), ('usage', 'in', ['customer', 'supplier'])]]
STEPS['step_38']['FIELDS'] = ['name', 'location_id', 'usage', 'company_id', 'out_partner_id', 'out_address_partner_id']
STEPS['step_38']['CHILD_FIELDS'] = []
STEPS['step_38']['SKIP_FIELDS'] = []
STEPS['step_38']['RELATIONAL_FIELDS'] = ['location_id', 'company_id', 'out_partner_id', 'out_address_partner_id']
STEPS['step_38']['FIELD_MAPPING'] = {
}
STEPS['step_38']['ORDER'] = 'id'
STEPS['step_38']['COMPARE_FILED'] = ''

# product.supplierinfo.pricelist
STEPS['step_39']['MODEL'] = 'product.supplierinfo.pricelist'
STEPS['step_39']['TARGET_MODEL'] = ''
STEPS['step_39']['SEARCH_DOMAIN'] = []
STEPS['step_39']['SEARCH_DOMAINS'] = [[]]
STEPS['step_39']['FIELDS'] = ['name', 'active', 'usage', 'company_id', 'partner_id', 'currency_id', 'sequence',
                              'date_start', 'date_end']
STEPS['step_39']['CHILD_FIELDS'] = []
STEPS['step_39']['SKIP_FIELDS'] = []
STEPS['step_39']['RELATIONAL_FIELDS'] = ['company_id', 'partner_id', 'currency_id', 'out_address_partner_id']
STEPS['step_39']['FIELD_MAPPING'] = {
}
STEPS['step_39']['ORDER'] = 'id'
STEPS['step_39']['COMPARE_FILED'] = ''

# product.supplierinfo
STEPS['step_40']['MODEL'] = 'product.supplierinfo'
STEPS['step_40']['TARGET_MODEL'] = ''
STEPS['step_40']['SEARCH_DOMAIN'] = [('pricelist_id', '!=', False)]
STEPS['step_40']['SEARCH_DOMAINS'] = [[]]
STEPS['step_40']['FIELDS'] = ['sequence', 'name', 'pricelist_id', 'product_name', 'product_code', 'product_uom',
                              'min_qty', 'price', 'currency_id', 'date_start', 'date_end', 'product_id',
                              'product_tmpl_id', 'delay']
STEPS['step_40']['CHILD_FIELDS'] = []
STEPS['step_40']['SKIP_FIELDS'] = []
STEPS['step_40']['RELATIONAL_FIELDS'] = ['pricelist_id', 'name', 'partner_id', 'product_uom', 'currency_id',
                                         'product_id', 'product_tmpl_id']
STEPS['step_40']['FIELD_MAPPING'] = {
    'name': 'partner_id',
}
STEPS['step_40']['ORDER'] = 'id'
STEPS['step_40']['COMPARE_FILED'] = ''

# stock.picking.type do nou use best prepare at manual
STEPS['step_41']['MODEL'] = 'stock.picking.type'
STEPS['step_41']['TARGET_MODEL'] = ''
STEPS['step_41']['SEARCH_DOMAIN'] = []
STEPS['step_41']['SEARCH_DOMAINS'] = [[]]
STEPS['step_41']['FIELDS'] = ['name', 'color', 'default_location_src_id', 'default_location_dest_id', 'code',
                              'return_picking_type_id', 'warehouse_id', 'use_create_lots', 'use_existing_lots',
                              'show_operations', 'show_reserved']
STEPS['step_41']['CHILD_FIELDS'] = []
STEPS['step_41']['SKIP_FIELDS'] = []
STEPS['step_41']['RELATIONAL_FIELDS'] = ['warehouse_id']
STEPS['step_41']['FIELD_MAPPING'] = {
}
STEPS['step_41']['ORDER'] = 'id'
STEPS['step_41']['COMPARE_FILED'] = ''

# stock.picking
STEPS['step_42']['MODEL'] = 'stock.picking'
STEPS['step_42']['TARGET_MODEL'] = ''
STEPS['step_42']['SEARCH_DOMAIN'] = [('company_id', '=', 6), ('purchase_id', '!=', False)]
STEPS['step_42']['SEARCH_DOMAINS'] = [[]]
STEPS['step_42']['FIELDS'] = ['name', 'origin', 'note', 'move_type', 'scheduled_date', 'date', 'state',
                              'date_done', 'location_id', 'location_dest_id', 'picking_type_id', 'picking_type_code',
                              'partner_id', 'company_id', 'sale_id', 'purchase_id']
# STEPS['step_42']['FIELDS'] = ['sale_id', 'purchase_id', 'scheduled_date', 'date', 'location_id', 'location_dest_id', 'picking_type_id']
STEPS['step_42']['CHILD_FIELDS'] = []
STEPS['step_42']['SKIP_FIELDS'] = []
STEPS['step_42']['EXCEPTION_FIELDS'] = [
    'scheduled_date', 'date',
]
STEPS['step_42']['RELATIONAL_FIELDS'] = ['location_id', 'location_dest_id', 'picking_type_id', 'partner_id', 'company_id', 'sale_id', 'purchase_id']
STEPS['step_42']['FIELD_MAPPING'] = {
}
STEPS['step_42']['ORDER'] = 'id'
STEPS['step_42']['COMPARE_FILED'] = ''

# stock.move
STEPS['step_43']['MODEL'] = 'stock.move'
STEPS['step_43']['TARGET_MODEL'] = ''
STEPS['step_43']['SEARCH_DOMAIN'] = [('company_id', '=', 6), ('purchase_line_id', '=', False)]
STEPS['step_43']['SEARCH_DOMAINS'] = [[]]
STEPS['step_43']['FIELDS'] = ['name', 'sequence', 'create_date', 'date', 'company_id', 'product_id', 'state',
                              'product_uom_qty', 'product_uom', 'location_id',
                              'location_dest_id', 'partner_id', 'picking_id', 'price_unit',
                              'origin', 'picking_type_id', 'warehouse_id', 'reference', 'purchase_line_id', 'sale_line_id']
STEPS['step_43']['CHILD_FIELDS'] = []
STEPS['step_43']['SKIP_FIELDS'] = []
STEPS['step_43']['EXCEPTION_FIELDS'] = [
    'create_date', 'date',
]
STEPS['step_43']['RELATIONAL_FIELDS'] = ['location_id', 'location_dest_id', 'product_uom', 'product_id', 'partner_id', 'company_id',
                                         'picking_id', 'picking_type_id', 'warehouse_id', 'purchase_line_id', 'sale_line_id']
STEPS['step_43']['FIELD_MAPPING'] = {
}
STEPS['step_43']['ORDER'] = 'id'
STEPS['step_43']['COMPARE_FILED'] = ''

# stock.move.line
STEPS['step_44']['MODEL'] = 'stock.move.line'
STEPS['step_44']['TARGET_MODEL'] = ''
STEPS['step_44']['SEARCH_DOMAIN'] = [('picking_id.company_id', '=', 6), ('move_id.purchase_line_id', '=', False), ('id', '>', 552780)]
STEPS['step_44']['SEARCH_DOMAINS'] = [[]]
STEPS['step_44']['FIELDS'] = ['picking_id', 'move_id', 'product_id', 'product_uom_id', 'product_uom_qty',
                              'qty_done', 'lot_id', 'date', 'location_id', 'location_dest_id', 'picking_id.company_id'
                              ]
STEPS['step_44']['CHILD_FIELDS'] = []
STEPS['step_44']['SKIP_FIELDS'] = []
STEPS['step_44']['RELATIONAL_FIELDS'] = ['picking_id',  'move_id', 'product_id', 'product_uom_id', 'lot_id', 'location_id',
                                         'location_dest_id', 'company_id']
STEPS['step_44']['FIELD_MAPPING'] = {
    'picking_id.company_id': 'company_id',
    'product_uom_qty': 'reserved_uom_qty',
}
STEPS['step_44']['ORDER'] = 'id'
STEPS['step_44']['COMPARE_FILED'] = ''

# account.invoice
STEPS['step_45']['MODEL'] = 'account.invoice'
STEPS['step_45']['TARGET_MODEL'] = 'account.move'
STEPS['step_45']['SEARCH_DOMAIN'] = [('company_id', '=', 6)]
STEPS['step_45']['SEARCH_DOMAINS'] = [[]]
STEPS['step_45']['FIELDS'] = ['picking_id', 'move_id', 'product_id', 'product_uom_id', 'product_uom_qty',
                              'qty_done', 'lot_id', 'date', 'location_id', 'location_dest_id', 'picking_id.company_id'
                              ]
STEPS['step_45']['CHILD_FIELDS'] = []
STEPS['step_45']['SKIP_FIELDS'] = []
STEPS['step_45']['RELATIONAL_FIELDS'] = ['picking_id',  'move_id', 'product_id', 'product_uom_id', 'lot_id', 'location_id',
                                         'location_dest_id', 'company_id']
STEPS['step_45']['FIELD_MAPPING'] = {
    'picking_id.company_id': 'company_id',
    'product_uom_qty': 'reserved_uom_qty',
}
STEPS['step_45']['ORDER'] = 'id'
STEPS['step_45']['COMPARE_FILED'] = ''

class OdooClient:
    odoo = None
    path = None

    def __init__(self, config_rpc):
        self.path = config_rpc.get('path') or False
        self.odoo = odoorpc.ODOO(config_rpc["url"], protocol=config_rpc["protocol"], port=int(config_rpc["port"]),
                                 timeout=600)

        self.odoo.login(config_rpc["db"], login=config_rpc["user"], password=config_rpc["password"])
        if self.odoo.env._context.get('lang') != RPC_LANG:
            self.odoo.env.context['lang'] = RPC_LANG

        # Set source instance language bg_BG, el_GR, en_US

        print(config_rpc.get('db'), config_rpc.get('user'), config_rpc.get('password'), self.odoo.env.user,
              self.odoo.env.context, self.odoo.env._context)
        # self.odoo.env['res.users'].write([self.rpc_user_id], {'lang': self.rpc_lang})

    def set_environment(self, ctx):
        ctx.update(self.odoo.env._context)
        self.odoo.env._context = ctx

    def search_and_read(self, search_read_model, search_read_domain, search_read_fields, limit=None, order='id',
                        sort_reverse=False):
        try:
            record_ids = self.odoo.env[search_read_model].search(search_read_domain, limit=limit, order=order)
            res = self.odoo.env[search_read_model].read(record_ids, search_read_fields) if record_ids else []

            # Check if order field exists in the results, then sort
            if res and order in res[0]:
                res = sorted(res, key=lambda x: x[order], reverse=sort_reverse)
            return res
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def search_and_browse(self, search_model, search_browse_domain, limit=None):
        record_ids = self.odoo.env[search_model].search(search_browse_domain, limit=limit)
        return self.odoo.env[search_model].browse(record_ids) if record_ids else []


def auto_get_fields(source, target):
    print('Configured fields #', FIELDS)
    source_model = MODEL
    target_model = TARGET_MODEL or MODEL
    source_model_id = source.search_and_read(
        'ir.model',
        [
            ('model', '=', source_model)
        ],
        ['name'])
    source_field_ids = source.search_and_read(
        'ir.model.fields',
        [
            ('model_id', '=', source_model_id['id'])
        ],
        ['name'])
    print("MODEL", source_model, source_model_id, source_field_ids)

    target_model_id = target.search_and_read(
        'ir.model',
        [
            ('model', '=', target_model)],
        ['name'])
    target_field_ids = source.search_and_read(
        'ir.model.fields',
        [
            ('model_id', '=', target_model_id['id'])
        ],
        ['name'])
    print("MODEL", target_model, target_model_id, target_field_ids)
    for field in source_field_ids:
        if field['name'] in target_field_ids:
            if not set(FIELDS).intersection(set(field['name'])):
                FIELDS.append(field['name'])
        elif field['name'] not in target_field_ids and FIELD_MAPPING.get(field['name']):
            FIELDS.append(field['name'])
    print('Used fields #', FIELDS)


def map_fields(source_record, field_mapping):
    dest_record = {}
    for src_field, value in source_record.items():
        # Map field if it is in the field mapping, otherwise keep the same field name
        dest_field = field_mapping.get(src_field, src_field)
        if src_field == 'description' and value:
            soup = BeautifulSoup(value, 'html.parser')
            value = soup.text
        dest_record[dest_field] = value
    return dest_record


def default_fields(source_record, default_data):
    for src_field, value in source_record.items():
        if default_data.get(src_field):
            source_record[src_field] = default_data[src_field]
    return source_record


def map_fields_id(source_record, field_id_mapping):
    dest_record = {}
    for src_field, value in source_record.items():
        dest_field_id = field_id_mapping.get(src_field)
        if dest_field_id:
            print(f'ID Mapping {src_field} {value} dest_field_id {dest_field_id}')
            if isinstance(value, list):
                for inx, val in enumerate(value):
                    base_inx = [(i, x) for i, x in enumerate(dest_field_id[0]) if x == val]
                    if base_inx:
                        if not FIELD_ID_MAPPING_SAVE.get(src_field):
                            FIELD_ID_MAPPING_SAVE[src_field] = set([])
                        FIELD_ID_MAPPING_SAVE[src_field].update(value)
                        # print(f"value {value} inx {inx} val {val} base_inx {base_inx} {dest_field_id[1]}")
                        value[inx] = dest_field_id[1][base_inx[0][0]]
            else:
                value = dest_field_id[1]
            print(f'ID Mapping {src_field} {value} {dest_field_id}')
        dest_record[src_field] = value
    return dest_record


def search_read_ir_model_data(relation_record, field_name, model, external_key=False, field_value=False):
    if not external_key and field_value:
        external_key = f'source_{model.replace(".", "_")}_{field_value[0]}'

    parent_id = odoo_dest.search_and_read(
        'ir.model.data',
        [
            ('name', '=', external_key),
            ('model', '=', model)],
        ['res_id'])
    # print(parent_id)
    if parent_id:
        relation_record[field_name] = parent_id[0]['res_id']
        check_target_record = odoo_dest.search_and_read(model,
                                                        [('id', '=', parent_id[0]['res_id'])],
                                                        ['name'])
        if not check_target_record:
            check_target_record_unlink = odoo_dest.odoo.env['ir.model.data'].search([('id', '=', parent_id[0]['id'])])
            check_target_record_unlink = odoo_dest.odoo.env['ir.model.data'].browse(check_target_record_unlink)
            print('Delete #', parent_id, check_target_record_unlink)
            check_target_record_unlink.unlink()
            relation_record['block'] = True
    else:
        relation_record['block'] = True
    print('Result relation#', model, external_key, relation_record.get('block') and 'for block' or 'for save', parent_id)


def auto_get_id(value, model=False):
    if not model:
        model = MODEL
    parent_id = odoo_dest.search_and_read(
        'ir.model.data',
        [
            ('name', '=', value),
            ('model', '=', model)],
        ['res_id'])
    return parent_id and parent_id[0]['res_id'] or False

def skip_fields(relation_record_for_skip):
    for skip_field in SKIP_FIELDS:
        if skip_field in relation_record_for_skip:
            del relation_record_for_skip[skip_field]
    return relation_record_for_skip

def process_relation_field(relation_record, field_name, relation_model, original_record):
    if field_name in relation_record:
        field_value = relation_record[field_name]
        print('Relation #:', field_name, field_value, VERSION_SRC, '=>', VERSION_DEST, display_processed_record(relation_record),  'relation_model', relation_model,
              'target model', TARGET_MODEL,
              'list', isinstance(field_value, list), 'tuple',
              isinstance(field_value, tuple))

        if not field_value and field_name in ['partner_patient_id', 'patient_partner_id']:
            parent_id = odoo_dest.search_and_read(
                'ir.model.data',
                [
                    ('name', '=', 'random_patient'),
                    ('module', '=', 'hospital'),
                    ('model', '=', 'res.partner')],
                ['res_id'])
            if parent_id:
                relation_record[field_name] = parent_id[0]['res_id']
                print("RES #", parent_id)
            else:
                relation_record['block'] = True

        if isinstance(field_value, (list, tuple)) \
                and len(list(filter(lambda x: isinstance(x, int), field_value))) != len(field_value):
            # If the field is a list or tuple (common in many2one relations), take the first element (ID)
            if field_name == 'parent_id':
                source_id = False
                if MODEL != 'res.partner':
                    source_id = odoo_src.search_and_read(
                        'ir.model.data',
                        [
                            ('res_id', '=', field_value[0]),
                            ('model', '=', relation_model)],
                        ['name', 'module'])
                    print('Source parent', source_id)
                if source_id and source_id[0]['module'] and (source_id[0]['module'] != '__export__' and source_id[0]['module'] != 'remote_multi_company'):
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', source_id[0]['name']),
                            ('model', '=', relation_model)],
                        ['res_id', 'name'])
                else:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_{MODEL.replace(".", "_")}_{field_value[0]}'),
                            ('model', '=', relation_model)],
                        ['res_id', 'name'])
                print('Parent after search', parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    # relation_record[field_name] = field_value[0]
                    relation_record['block'] = True
                print(field_name, relation_model, field_value, relation_record[field_name])

            elif field_name == 'patient_data_file_id':
                search_read_ir_model_data(relation_record, field_name, 'patient.data', field_value=field_value)
                if relation_record.get('block'):
                    del relation_record['patient_data_file_id']

            elif field_name in ['partner_id', 'partner_invoice_id', 'partner_shipping_id', 'partner_doctor_id',
                                'contact_id', 'manufacturer', 'partner_patient_id', 'patient_partner_id',
                                'out_partner_id', 'out_address_partner_id', 'dest_address_id']:
                search_read_ir_model_data(relation_record, field_name, 'res.partner', field_value=field_value)
                if relation_record.get('block'):
                    no_more = False
                    if field_value[0] == 1:
                        relation_record[field_name] = 1
                        del relation_record['block']
                        no_more = True

                    if field_name in ['partner_patient_id', 'patient_partner_id']:
                        parent_id = odoo_dest.search_and_read(
                            'ir.model.data',
                            [
                                ('name', '=', 'random_patient'),
                                ('module', '=', 'hospital'),
                                ('model', '=', 'res.partner')],
                            ['res_id'])
                        if parent_id:
                            relation_record[field_name] = parent_id[0]['res_id']
                            del relation_record['block']
                        else:
                            relation_record['block'] = True
                            no_more = True
                        # print('patient_partner_id #', parent_id, no_more, relation_record)

                    if not no_more:
                        vat = odoo_src.search_and_read(
                            'res.partner',
                            [
                                ('id', '=', field_value[0]),
                            ],
                            ['vat'])
                        if vat:
                            parent_id = odoo_dest.search_and_read(
                                'res.partner',
                                [
                                    ('vat', '=', vat[0]['vat'])],
                                ['name'], limit=1)
                        ref = odoo_src.search_and_read(
                            'res.partner',
                            [
                                ('id', '=', field_value[0]),
                            ],
                            ['ref'])
                        if ref:
                            parent_id = odoo_dest.search_and_read(
                                'res.partner',
                                [
                                    ('ref', '=', ref[0]['ref'])],
                                ['name'], limit=1)

            elif field_name in ['product_manufacturer_id', 'manufacturer_id']:
                search_read_ir_model_data(relation_record, field_name, 'product.manufacturer', field_value=field_value)

            elif field_name == 'product_tmpl_id' and relation_model == 'product.packaging.type':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_template_{field_value[0]}'),
                        ('model', '=', 'product.template')],
                    ['res_id'])
                print("product_tmpl_id in product.packaging.type", parent_id)
                del relation_record['product_tmpl_id']
                if parent_id:
                    parent_id = odoo_dest.search_and_read(
                        'product.template',
                        [
                            ('id', '=', parent_id[0]['res_id'])
                            ],
                        ['product_variant_id'])
                    print("product_variant_id", parent_id)
                    if parent_id:
                        relation_record['product_id'] = parent_id[0]['product_variant_id'][0]
                        print("original_record", original_record)
                else:
                    relation_record['block'] = True

            elif field_name == 'product_tmpl_id' and not relation_model == 'product.packaging.type':
                search_read_ir_model_data(relation_record, field_name, 'product.template', field_value=field_value)

            elif field_name == 'employee_id':
                search_read_ir_model_data(relation_record, field_name, 'hr.employee', field_value=field_value)

            elif field_name == 'picking_type_id':
                search_read_ir_model_data(relation_record, field_name, 'stock.picking.type', field_value=field_value)

            elif field_name == 'picking_id':
                search_read_ir_model_data(relation_record, field_name, 'stock.picking', field_value=field_value)

            elif field_name == 'move_id':
                search_read_ir_model_data(relation_record, field_name, 'stock.move', field_value=field_value)

            elif field_name == 'fiscal_position_id':
                search_read_ir_model_data(relation_record, field_name, 'account.fiscal.position', field_value=field_value)

            elif field_name in ['product_id', 'product_variant_id']:
                search_read_ir_model_data(relation_record, field_name, 'product.product', field_value=field_value)

            elif field_name == 'lot_id':
                data_model = 'stock.lot'
                external_key = f'source_{data_model.replace(".", "_")}_{field_value[0]}'

                if VERSION_SRC <= 11 and VERSION_DEST >= 16:
                    external_key = f'source_{"stock.production.lot".replace(".", "_")}_{field_value[0]}'

                if VERSION_SRC <= 11 and VERSION_DEST <= 11:
                    data_model = 'stock.production.lot'
                    external_key = f'source_{data_model.replace(".", "_")}_{field_value[0]}'

                search_read_ir_model_data(relation_record, field_name, data_model, external_key=external_key)

            elif field_name == 'bom_id':
                search_read_ir_model_data(relation_record, field_name, 'mrp.bom', field_value=field_value)

            elif field_name in ['location_id', 'location_dest_id']:
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_stock_location_{field_value[0]}'),
                        ('model', '=', 'stock.location')],
                    ['res_id'])
                print('Result relation#', relation_model, f'source_stock_location_{field_value[0]}', parent_id, f'source_stock_location_{field_value[0]}')
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    source_id = odoo_src.search_and_read(
                        'ir.model.data',
                        [
                            ('res_id', '=', field_value[0]),
                            ('model', '=', 'stock.location')],
                        ['name', 'module'])
                    print('source_id stock.location', source_id)
                    if source_id:
                        parent_id = odoo_dest.search_and_read(
                            'ir.model.data',
                            [
                                ('name', '=', f'{source_id[0]["name"]}'),
                                ('model', '=', 'stock.location')],
                            ['res_id'])
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True

            elif field_name == 'company_id' and field_value[0] != 1:
                search_read_ir_model_data(relation_record, field_name, 'res.company', field_value=field_value)

            elif field_name == 'product_set_id':
                search_read_ir_model_data(relation_record, field_name, 'product.set', field_value=field_value)

            elif field_name == 'pricelist_id' and TARGET_MODEL == 'product.set.pricelist':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_pricelist_{field_value[0]}'),
                        ('model', '=', 'product.pricelist'),
                        # ('company_id', '=', relation_record['company_id']),
                    ],
                    ['res_id'])
                if parent_id:
                    product_set_pricelist_id = odoo_dest.search_and_read(
                        'product.pricelist',
                        [
                            ('id', '=', parent_id[0]['res_id']),
                        ],
                        ['company_id', 'currency_id'])
                    if product_set_pricelist_id:
                        relation_record[field_name] = parent_id[0]['res_id']
                        relation_record['company_id'] = product_set_pricelist_id[0]['company_id'][0]
                        relation_record['currency_id'] = product_set_pricelist_id[0]['currency_id'][0]
                else:
                    relation_record['block'] = True
                print('Relation: product.set.pricelist #', parent_id, f'source_product_pricelist_{field_value[0]}')

            elif field_name == 'pricelist_id' and relation_model == 'product.supplierinfo':
                search_read_ir_model_data(relation_record, field_name, 'product.supplierinfo.pricelist', field_value=field_value)

            elif field_name == 'pricelist_id' and TARGET_MODEL != 'product.set.pricelist':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_pricelist_{field_value[0]}'),
                        ('model', '=', 'product.pricelist'),
                        # ('company_id', '=', relation_record['company_id']),
                    ],
                    ['res_id'])

                if parent_id:
                    if original_record.get('company_id'):
                        company_id = odoo_dest.search_and_read(
                            'ir.model.data',
                            [
                                ('name', '=', f'source_res_company_{original_record["company_id"][0]}'),
                                ('model', '=', 'res.company'),
                            ],
                            ['res_id'])
                        print(f'company_id: {company_id}', original_record["company_id"])
                        if company_id:
                            company_parent_id = odoo_dest.search_and_read(
                                'product.pricelist',
                                [
                                    ('id', '=', parent_id[0]['res_id']),
                                    ('company_id', '=', company_id[0]['res_id']),
                                ],
                                ['id'])
                            print(f"company_parent_id: {company_parent_id}")
                            if company_parent_id:
                                relation_record[field_name] = company_parent_id[0]['id']
                            else:
                                relation_record['block'] = True
                    else:
                        relation_record[field_name] = parent_id[0]['res_id']
                        pricelist_id = odoo_dest.search_and_read(
                            'product.pricelist',
                            [
                                ('id', '=', parent_id[0]['res_id']),
                                # ('company_id', '=', relation_record['company_id']),
                            ],
                            ['company_id'])
                        company_id = odoo_dest.search_and_read(
                            'ir.model.data',
                            [
                                ('name', '=', f'source_res_company_{pricelist_id[0]["company_id"][0]}'),
                                ('model', '=', 'res.company'),
                            ],
                            ['res_id'])
                        print(f'company_id: {company_id}')
                        if company_id:
                            relation_record['company_id'] = company_id[0]['res_id']
                        else:
                            relation_record['block'] = True
                else:
                    relation_record['block'] = True

            elif field_name == 'sale_id' and relation_model == 'stock.picking':
                search_read_ir_model_data(relation_record, field_name, 'sale.order', field_value=field_value)

            elif field_name == 'purchase_id' and relation_model == 'stock.picking':
                search_read_ir_model_data(relation_record, field_name, 'purchase.order', field_value=field_value)

            elif field_name == 'purchase_line_id' and relation_model in ['stock.move']:
                search_read_ir_model_data(relation_record, field_name, 'purchase.order.line', field_value=field_value)

            elif field_name == 'sale_line_id' and relation_model in ['stock.move']:
                search_read_ir_model_data(relation_record, field_name, 'sale.order.line', field_value=field_value)

            elif field_name == 'order_id' and relation_model == 'sale.order.line':
                search_read_ir_model_data(relation_record, field_name, 'sale.order', field_value=field_value)

            elif field_name == 'order_id' and relation_model == 'purchase.order.line':
                search_read_ir_model_data(relation_record, field_name, 'purchase.order', field_value=field_value)

            elif field_name == 'manufacturer_id':
                search_read_ir_model_data(relation_record, field_name, 'product.manufacturer', field_value=field_value)

            elif field_name == 'routing_id':
                search_read_ir_model_data(relation_record, field_name, 'mrp.routing', field_value=field_value)

            elif field_name == 'workcenter_id':
                search_read_ir_model_data(relation_record, field_name, 'mrp.workcenter', field_value=field_value)

            elif field_name == 'product_set_id':
                search_read_ir_model_data(relation_record, field_name, 'product.set', field_value=field_value)

            elif field_name == 'attribute_id':
                search_read_ir_model_data(relation_record, field_name, 'product.attribute', field_value=field_value)

            elif field_name == 'category_id' and MODEL == 'product.uom':
                search_read_ir_model_data(relation_record, field_name, 'uom.uom', field_value=field_value)

            elif field_name == 'categ_id' and relation_model == 'product.template':
                source_id = odoo_src.search_and_read(
                    'ir.model.data',
                    [
                        ('res_id', '=', field_value[0]),
                        ('model', '=', 'product.category')],
                    ['name', 'module'])
                print('Source category', source_id)
                if source_id and (source_id[0]['module'] != '__export__' and source_id[0]['module'] != 'remote_multi_company'):
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', source_id[0]['name']),
                            ('model', '=', 'product.category')],
                        ['res_id'])
                else:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_category_{field_value[0]}'),
                            ('model', '=', 'product.category')],
                        ['res_id'])
                # print(parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']

            elif field_name == 'categ_id' and relation_model == 'product.packaging.type':
                source_id = odoo_src.search_and_read(
                    'ir.model.data',
                    [
                        ('res_id', '=', field_value[0]),
                        ('model', '=', 'product.category.packaging.type')],
                    ['name', 'module'])
                print('Source category', source_id)
                if source_id and (source_id[0]['module'] != '__export__' and source_id[0]['module'] != 'remote_multi_company'):
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', source_id[0]['name']),
                            ('model', '=', 'product.category.packaging.type')],
                        ['res_id'])
                else:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_category_packaging_type_{field_value[0]}'),
                            ('model', '=', 'product.category.packaging.type')],
                        ['res_id'])
                # print(parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']

            elif field_name in ['uom_po_id', 'uom_id', 'product_uom']:
                source_id = odoo_src.search_and_read(
                    'ir.model.data',
                    [
                        ('res_id', '=', field_value[0]),
                        ('model', 'in', ['product.uom', 'uom.uom'])],
                    ['name', 'module'])
                print('Source uom', source_id, field_value)
                if source_id and (source_id[0]['module'] != '__export__' and source_id[0]['module'] != 'remote_multi_company'):
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', source_id[0]['name']),
                            ('model', 'in', ['uom.uom', 'product.uom'])],
                        ['res_id'])
                else:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_uom_{field_value[0]}'),
                            ('model', '=', 'product.uom')],
                        ['res_id'])
                # print(parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True

            elif MODEL == 'product.properties.static':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_properties_static_dropdown_{field_value[0]}'),
                        ('model', '=', 'product.properties.static.dropdown')],
                    ['res_id'])
                print("product.properties.static", parent_id, field_name, field_value[0],
                      f'source_product_properties_static_dropdown_{field_value[0]}')
                relation_record[field_name] = parent_id[0]['res_id']
            else:
                relation_record[field_name] = field_value[0]

        elif isinstance(field_value, (list, tuple)) \
                and len(list(filter(str.isdigit, map(str, field_value)))) == len(field_value):
            ids_parent = []
            many2many = False
            if field_name == 'attribute_line_ids':
                if ACTION == 'delete':
                    relation_record[field_name] = False
                    field_value = []
                for id_res in field_value:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_template_attribute_line_{id_res}'),
                            ('model', '=', 'product.template.attribute.line')],
                        ['res_id'])
                    if parent_id:
                        ids_parent.append(parent_id[0]['res_id'])
                    else:
                        relation_record['block'] = True
                print('attribute_line_ids for skip #', field_value, 'replaced', ids_parent)
            elif field_name == 'assistant_contact_ids':
                for id_res in field_value:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_res_partner_{id_res}'),
                            ('model', '=', 'res.partner')],
                        ['res_id'])
                    if parent_id:
                        ids_parent.append(parent_id[0]['res_id'])

            elif field_name == 'product_id':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_product_{field_value[0]}'),
                        ('model', '=', 'product.product')],
                    ['res_id'])
                print('Relation #: product_id', parent_id, f'source_product_product_{field_value[0]}')
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True

            elif field_name == 'reelpackaging_ids':
                for key in relation_record[field_name]:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_packaging_type_{key}'),
                            ('model', '=', 'product.packaging.type')],
                        ['res_id'])
                    if parent_id:
                        many2many = True
                        ids_parent.append(parent_id[0]['res_id'])
            elif field_name == 'order_ids':
                for key in relation_record[field_name]:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_sale_order_{key}'),
                            ('model', '=', 'sale.order')],
                        ['res_id'])
                    if parent_id:
                        many2many = True
                        ids_parent.append(parent_id[0]['res_id'])
                        order_id = odoo_dest.search_and_read(
                            'sale.order',
                            [
                                ('id', '=', parent_id[0]['res_id'])],
                            ['company_id', 'partner_doctor_id'])
                        print('order_id', order_id, parent_id)
                        relation_record['company_id'] = order_id[0]['company_id'][0]
                        relation_record['partner_doctor_id'] = order_id[0]['partner_doctor_id'][0]
                if not relation_record[field_name] or not ids_parent:
                    source_id = odoo_src.search_and_read(
                        'sale.order',
                        [
                            ('patient_data_file_id', '=', relation_record['id']),
                        ],
                        ['name', 'company_id', 'partner_doctor_id'])
                    if source_id:
                        parent_id = odoo_dest.search_and_read(
                            'ir.model.data',
                            [
                                ('name', '=', f'source_sale_order_{source_id[0]["id"]}'),
                                ('model', '=', 'sale.order')],
                            ['res_id'])
                    else:
                        parent_id = False
                    print('patient_data_file_id sale.order', source_id, parent_id, relation_record['id'])
                    if parent_id:
                        # relation_record['order_ids'] = [parent_id[0]['res_id']]
                        ids_parent = [parent_id[0]['res_id']]
                        relation_record['company_id'] = source_id[0]['company_id'][0]
                        # relation_record['partner_doctor_id'] = source_id[0]['partner_doctor_id'][0]
                        relation_record['block'] = True
                    else:
                        relation_record['block'] = True
                print('Result relation # order_ids:', relation_model, ids_parent)

            elif field_name == 'value_ids':
                for id_res in field_value:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_attribute_value_{id_res}'),
                            ('model', '=', 'product.attribute.value')],
                        ['res_id'])
                    if parent_id:
                        ids_parent.append(parent_id[0]['res_id'])
            elif field_name == 'product_template_attribute_value_ids':
                # origin_product_tmpl_id = relation_record["product_tmpl_id"]
                #
                product_tmpl_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_template_{relation_record["product_tmpl_id"][0]}'),
                        ('model', '=', 'product.template')],
                    ['res_id'])
                print('product_tmpl_id in product_template_attribute_value_ids', product_tmpl_id, original_record["product_tmpl_id"])
                if product_tmpl_id:
                    relation_record['product_tmpl_id'] = product_tmpl_id[0]['res_id']
                # else:
                #     relation_record['product_tmpl_id'] = origin_product_tmpl_id[0]

                for id_res in field_value:
                    # get from origin
                    origin_product_attribute_value_id = odoo_src.search_and_read(
                        'product.attribute.value',
                        [
                            ('id', '=', id_res),
                        ],
                        ['name', 'attribute_id', 'name'],
                        order='id')
                    # attribute id
                    print('origin_product_attribute_value_id', origin_product_attribute_value_id, id_res)
                    if origin_product_attribute_value_id:
                        attribute_id = odoo_dest.search_and_read(
                            'ir.model.data',
                            [
                                ('name', '=',
                                 f'source_product_attribute_{origin_product_attribute_value_id[0]["attribute_id"][0]}'),
                                ('model', '=', 'product.attribute')],
                            ['res_id'])
                        dest_attribute_id = odoo_dest.search_and_read(
                            'product.attribute',
                            [
                                ('id', '=', attribute_id[0]['res_id']),
                            ],
                            ['name'],
                            order='id')
                    else:
                        attribute_id = dest_attribute_id = False
                    # value id
                    product_attribute_value_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_attribute_value_{id_res}'),
                            ('model', '=', 'product.attribute.value'),
                        ],
                        ['res_id'])
                    if product_attribute_value_id:
                        dest_product_attribute_value_id = odoo_dest.search_and_read(
                            'product.attribute.value',
                            [
                                ('id', '=', product_attribute_value_id[0]['res_id']),
                            ],
                            ['name', 'attribute_id'],
                            order='id')
                    else:
                        dest_product_attribute_value_id = []
                        relation_record['block'] = True

                    print('\n')
                    print('Attribute filter #:')
                    print('dest_product_attribute_value_id', dest_product_attribute_value_id)
                    print('product_tmpl_id', relation_record["product_tmpl_id"])
                    print('product_tmpl_id dist', product_tmpl_id, f'source_product_template_{relation_record["product_tmpl_id"]}')
                    # print('origin_product_tmpl_id', origin_product_tmpl_id)
                    print('origin_product_attribute_value_id', origin_product_attribute_value_id)

                    print('product_attribute_value_id', product_attribute_value_id)
                    print('attribute_id', attribute_id)
                    print('dest_attribute_id', dest_attribute_id)
                    # print('attribute_line_id', attribute_line_id)
                    if product_attribute_value_id and attribute_id:
                        product_template_attribute_value_id = odoo_dest.search_and_read(
                            'product.template.attribute.value',
                            [
                                ('product_attribute_value_id', '=', product_attribute_value_id[0]['res_id']),
                                ('attribute_id', '=', attribute_id[0]['res_id']),
                                ('product_tmpl_id', '=', relation_record["product_tmpl_id"]),
                            ],
                            ['name'])
                    else:
                        product_template_attribute_value_id = []
                        relation_record['block'] = True

                    print('Attribute value #:', product_template_attribute_value_id)
                    if product_template_attribute_value_id:
                        ids_parent.append(product_template_attribute_value_id[0]['id'])

            if ids_parent:
                print('IDS', ids_parent)
                if many2many:
                    relation_record[field_name] = [(6, 0, ids_parent)]
                else:
                    relation_record[field_name] = ids_parent

        elif isinstance(field_value, (list, tuple)) and len(field_value) == 1:
            # If it's a single element list/tuple, unpack the single value
            relation_record[field_name] = field_value[0]

        elif field_name == 'object_id' and relation_record['object_id'].split(',')[0] == 'product.product':
            # print('object_id', relation_record['object_id'])
            parent_id = product_product_id = False
            source_model, source_res_id = relation_record['object_id'].split(',')
            source_id = odoo_src.search_and_read(
                source_model,
                [
                    ('id', '=', source_res_id)
                ],
                ['name', 'product_tmpl_id'])
            # print('object_id',
            #       relation_record['object_id'],
            #       source_model,
            #       source_res_id,
            #       f'source_product_product_{source_id[0]["id"]}',
            #       f'source_product_template_{source_id[0]["product_tmpl_id"][0]}',
            #       source_id[0]['product_tmpl_id'])
            if source_id:
                product_product_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_product_{source_id[0]["id"]}'),
                        ('model', '=', 'product.product')],
                    ['res_id'])
            if source_id:
                if not product_product_id:
                    product_tmpl_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_template_{source_id[0]["product_tmpl_id"][0]}'),
                            ('model', '=', 'product.template')],
                        ['res_id'])
                    print('product_tmpl_id', product_tmpl_id)
                    if product_tmpl_id:
                        parent_id = odoo_dest.search_and_read(
                            'product.product',
                            [
                                ('product_tmpl_id', '=', product_tmpl_id[0]['res_id'])
                            ],
                            ['product_prop_static_id', 'product_tmpl_id'], limit=1)
                else:
                    parent_id = odoo_dest.search_and_read(
                        'product.product',
                        [
                            ('id', '=', product_product_id[0]['res_id'])
                        ],
                        ['product_prop_static_id'])
            if parent_id:
                relation_record['product_prop_static_id'] = parent_id[0]['product_prop_static_id'][0]
                existing_id = odoo_dest.search_and_read('ir.model.data',
                                                        [
                                                            ('name', '=',
                                                             f'source_{MODEL.replace(".", "_")}_{relation_record["id"]}'),
                                                            ('model', '=', MODEL)
                                                        ],
                                                        ['res_id'])
                if not existing_id:
                    odoo_dest.odoo.env['ir.model.data'].create({
                        'name': f'source_{MODEL.replace(".", "_")}_{relation_record["id"]}',
                        'model': MODEL,
                        'module': 'remote_multi_company',
                        'res_id': relation_record['product_prop_static_id'],
                    })

                del relation_record['object_id']
                del relation_record['product_prop_static_id']
            else:
                relation_record['block'] = True

        elif field_name == 'object_id' and relation_record['object_id'].split(',')[0] == 'product.template':
            # print('object_id', relation_record['object_id'])
            parent_id = product_product_id = False
            source_model, source_res_id = relation_record['object_id'].split(',')
            source_id = odoo_src.search_and_read(
                source_model,
                [
                    ('id', '=', source_res_id)
                ],
                ['name'])
            if source_id:
                product_product_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_template_{source_id[0]["id"]}'),
                        ('model', '=', 'product.template')],
                    ['res_id'])
            if source_id:
                parent_id = odoo_dest.search_and_read(
                    'product.template',
                    [
                        ('id', '=', product_product_id[0]['res_id'])
                    ],
                    ['product_prop_static_id'])
            if parent_id and parent_id[0]['product_prop_static_id']:
                print('parent_id', parent_id)
                relation_record['product_prop_static_id'] = parent_id[0]['product_prop_static_id'][0]
                existing_id = odoo_dest.search_and_read('ir.model.data',
                                                        [
                                                            ('name', '=',
                                                             f'source_{MODEL.replace(".", "_")}_{relation_record["id"]}'),
                                                            ('model', '=', MODEL)
                                                        ],
                                                        ['res_id'])
                if not existing_id:
                    odoo_dest.odoo.env['ir.model.data'].create({
                        'name': f'source_{MODEL.replace(".", "_")}_{relation_record["id"]}',
                        'model': MODEL,
                        'module': 'remote_multi_company',
                        'res_id': relation_record['product_prop_static_id'],
                    })

                del relation_record['object_id']
                del relation_record['product_prop_static_id']
            else:
                relation_record['block'] = True


def process_record(active_model, active_record, original_record):
    for field in RELATIONAL_FIELDS:
        process_relation_field(active_record, field, active_model, original_record)

    # Check and modify the active record based on specific conditions
    if active_model == 'res.partner':  # Example for 'res.partner' active model
        # Check if 'company_type' is neither 'person' nor 'company'
        if active_record.get('type') == 'doctor':
            active_record['type'] = 'contact'
            active_record['medical_type'] = 'doctor'
        if active_record.get('type') == 'patient':
            active_record['type'] = 'contact'
            active_record['medical_type'] = 'patient'
        if active_record.get('type') == 'hospital':
            active_record['type'] = 'contact'
            active_record['medical_type'] = 'hospital'
        if active_record.get('l10n_bg_uic'):
            if not list(filter(str.isdigit, active_record['l10n_bg_uic'])):
                active_record['l10n_bg_uic'] = active_record.get('vat')
            # print(active_record['vat'], active_record['l10n_bg_uic'])

            if not active_record['vat'] and not active_record['l10n_bg_uic']:
                return active_record

            prefix = active_record['vat'] and active_record['vat'][:2] or active_record['l10n_bg_uic'][:2]
            if active_record.get('l10n_bg_uic') == active_record['vat'] \
                    and active_record['l10n_bg_uic'].upper().startswith('BG'):
                active_record['l10n_bg_uic'] = active_record['l10n_bg_uic'][2:]
            if prefix.upper() == 'BG':
                active_record['l10n_bg_uic_type'] = 'bg_uic'
            elif list(filter(str.isdigit, prefix)) and int(prefix) != 99 and len(active_record['l10n_bg_uic']) == 10 \
                    and active_record.get('country_id') and active_record['country_id'] == 22:
                active_record['l10n_bg_uic_type'] = 'bg_egn'
            elif list(filter(str.isdigit, prefix)) and int(prefix) != 99 and active_record.get('country_id') \
                    and active_record['country_id'] == 22:
                active_record['l10n_bg_uic_type'] = 'bg_uic'
            elif list(filter(str.isdigit, prefix)) and int(prefix) == 99:
                active_record['l10n_bg_uic_type'] = 'bg_non_eu'
            else:
                active_record['l10n_bg_uic_type'] = 'eu_vat'
        if active_record.get('vat') and active_record.get('parent_id'):
            del active_record['vat']
    elif active_model == 'product.attribute':
        active_record['create_variant'] = 'dynamic'
    elif active_model == 'product.pricelist.item' and active_record.get('base') and active_record[
        'base'] == 'competitorinfo':
        active_record['block'] = True
    elif active_record.get('currency_id') and active_record['currency_id'] == 27:
        active_record['currency_id'] = 26
    elif active_model == 'product.attribute.value' and TARGET_MODEL:
        ids_product = set([])
        attribute_id = odoo_dest.search_and_read(
            'ir.model.data',
            [
                ('name', '=', f'source_product_attribute_{active_record["attribute_id"]}'),
                ('model', '=', 'product.attribute')],
            ['res_id'])
        for product_id in active_record['product_ids']:
            id_product = odoo_dest.search_and_read(
                'ir.model.data',
                [
                    ('name', '=', f'source_product_product_{product_id}'),
                    ('model', '=', 'product.product')],
                ['res_id'])
            print(f"id_product: {id_product}")
            if id_product:
                id_product = odoo_dest.search_and_read(
                    'product.product',
                    [
                        ('id', '=', id_product[0]['res_id'])
                    ],
                    ['product_tmpl_id'])
                ids_product.update([id_product[0]['product_tmpl_id'][0]])
        attribute_line_id = odoo_dest.search_and_read(
            'product.template.attribute.line',
            [
                ('attribute_id', '=', attribute_id[0]['res_id']),
                ('product_tmpl_id', 'in', list(ids_product))
            ],
            ['attribute_id'],
            order='id')
        if attribute_line_id:
            active_record['attribute_line_id'] = attribute_line_id[0]['id']
    return active_record


def _ids2str(ids):
    return ','.join([str(i) for i in sorted(ids)])


def display_processed_record(processed_record):
    return {k: v for k, v in processed_record.items() if k not in ['datas', 'image', 'image_1920']}


def process_step_mode_1(step):
    # Load configuration from file
    counter = 0
    parent_ids = []
    last_id = 0
    start = True
    skips_ids = []
    parent_direction = 'not in'
    if MODEL == 'res.partner':
        source_parent_ids = odoo_src.search_and_read('res.company', [], ['partner_id'], order='id')
        print('Skip company ids', source_parent_ids)
        parent_ids = [x['partner_id'][0] for x in source_parent_ids]
        child_ids = odoo_src.search_and_read('res.partner', [('parent_id', 'in', parent_ids)], [], order='id')
        parent_ids += [x['id'] for x in child_ids]
    elif MODEL in ('product.category', 'product.product', 'product.uom.categ'):
        # Get standard ids
        source_parent_ids = odoo_src.search_and_read('ir.model.data',
                                                     ["&", ('module', '!=', '__export__'), ('module', '!=', 'remote_multi_company'), ('model', '=', MODEL)],
                                                     ['res_id'], order='id')
        parent_ids = [x['res_id'] for x in source_parent_ids]
    elif MODEL == 'product.template':
        category_ids = []
        for category in PRODUCT_CATEGORY:
            category_ids = odoo_src.search_and_read('product.category',
                                                    [('complete_name', 'like', category)],
                                                    ['id'], order='complete_name')
            # exclusive_category_ids = [x['id'] for x in category_ids]
            category_ids = [x['id'] for x in category_ids]
            # print(category_ids)
        if category_ids:
            product_ids = odoo_src.search_and_read('product.template',
                                                   [('categ_id', 'not in', category_ids)],
                                                   ['id'], order='id')
            parent_ids = [x['id'] for x in product_ids]
            parent_direction = 'not in'
    else:
        parent_ids = False

    order_batch = ORDER.split(',')[0].split(' ')
    if len(order_batch) > 1:
        direction = order_batch[1] == 'desc' and '<' or '>'
        order_batch_field = order_batch[0]
    else:
        direction = '>'
        order_batch_field = order_batch[0]

    for search_domain in SEARCH_DOMAINS:
        while start:
            if parent_ids:
                search_domain += [('id', parent_direction, parent_ids)]
            # print('Search domain', SEARCH_DOMAIN, search_domain)
            # Fetch data from source
            batch_domain = last_id == 0 and [] or [(order_batch_field, direction, last_id)]
            print("Search domain #", batch_domain + SEARCH_DOMAIN + search_domain)
            source_data = odoo_src.search_and_read(MODEL, batch_domain + SEARCH_DOMAIN + search_domain,
                                                   FIELDS, limit=100, order=ORDER)
            if not source_data:
                start = False
                break
            # Process and import/update in destination
            for record in source_data:
                last_id = record.get(order_batch_field) or record['id']
                record = skip_fields(record)

                if MODEL == 'product.properties.static':
                    if len([f"{k}:{v}" for k, v in record.items() if k not in ['id', 'object_id'] and v]) == 0 \
                            or not record['object_id']:
                        skips_ids.append(record['id'])
                        print("Skip record #:", record['id'])
                        continue

                print('Record #:',
                      TARGET_MODEL or MODEL,
                      f"{record['id']}=>{last_id}",
                      display_processed_record(record))
                os.environ['CURRENT_ROW'] = f"{record['id']}"
                mapped_record = map_fields(record, FIELD_MAPPING)  # Pass the field_mapping dictionary here
                print('mapped_record #', FIELD_MAPPING, mapped_record)
                mapped_record = default_fields(mapped_record, DEFAULT_FIELDS)  # replace with default data
                processed_record = process_record(MODEL, mapped_record, record)  # Process the record
                processed_record = map_fields_id(processed_record, FIELD_ID_MAPPING) # Process the id mapping
                if processed_record.get('block'):
                    print("Skip", display_processed_record(processed_record))
                    BLOCKED_FIELDS.append(processed_record.get('name') or processed_record.get('display_name') or processed_record.get('default_code'))
                    continue
                del processed_record['id']

                # print('Record to save #:', processed_record.keys())
                if processed_record.get('partner_doctor_id', None) is not None and not processed_record.get(
                        'partner_doctor_id'):
                    processed_record.update({'partner_doctor_id': processed_record.get('partner_id')})
                    print(f"Processed record is replaced with: {processed_record['partner_doctor_id']}")

                if processed_record.get('applied_on', False) == '3_global':
                    continue
                target_model = TARGET_MODEL or MODEL

                if MODEL == 'product.manufacturer.datasheets':
                    res_res_id = odoo_dest.search_and_read('ir.model.data',
                                                           [
                                                               ('name', '=',
                                                                f'source_product_product_{record["res_id"]}'),
                                                               ('model', '=', 'product.product')
                                                           ],
                                                           ['res_id'])
                    if res_res_id:
                        processed_record['res_id'] = res_res_id[0]['res_id']
                    file = odoo_src.odoo.env[MODEL].browse(processed_record['id'])
                    processed_record['datas'] = file.datas

                print(f'Version: {odoo_src.odoo.version.split(".")} => {odoo_dest.odoo.version.split(".")}')
                if MODEL == 'product.product' and int(odoo_dest.odoo.version.split(".")[0]) >= 15:
                    ids_str = odoo_dest.search_and_read(
                        'product.product',
                        [
                            ('product_tmpl_id', '=', processed_record['product_tmpl_id']),
                            ('combination_indices', '=',
                             _ids2str(processed_record['product_template_attribute_value_ids']))
                        ],
                        ['name']
                    )
                    if ids_str:
                        print('Skip record', ids_str[0]['name'])
                        continue
                    if not processed_record['product_template_attribute_value_ids']:
                        continue
                # Search for existing external_id in the destination database
                existing_id = odoo_dest.search_and_read('ir.model.data',
                                                        [
                                                            ('name', '=',
                                                             f'source_{MODEL.replace(".", "_")}_{record["id"]}'),
                                                            ('model', '=', target_model)
                                                        ],
                                                        ['res_id', 'model', 'name'])
                if not existing_id and COMPARE_FILED and record.get(COMPARE_FILED):
                    print('Skip compare record', record[COMPARE_FILED].strip())
                    target_id = odoo_dest.search_and_read(target_model,
                                                          [
                                                              (COMPARE_FILED, '=', record[COMPARE_FILED].strip()),
                                                          ],
                                                          [COMPARE_FILED]
                                                          )
                    if target_id:
                        print('Target record', target_id)
                        model_data_id = odoo_dest.search_and_read('ir.model.data',
                                                                  ('res_id', '=', target_id[0]['id']),
                                                                  ['res_id']
                                                                  )
                        if model_data_id:
                            model_data_id = odoo_dest.odoo.env['ir.model.data'].browse(model_data_id[0]['id'])
                            model_data_id.unlink()
                        # odoo_dest.odoo.env['ir.model.data'].create({
                        #     'name': f'source_{MODEL.replace(".", "_")}_{record["id"]}',
                        #     'model': target_model,
                        #     'module': 'remote_multi_company',
                        #     'res_id': target_id[0]['id'],
                        # })
                        # continue
                if existing_id:
                    check_target_record = odoo_dest.search_and_read(existing_id[0]['model'], [('id', '=', existing_id[0]['res_id'])], ['name'])
                    if not check_target_record:
                        check_target_record_unlink = odoo_dest.odoo.env['ir.model.data'].search([('id', '=', existing_id[0]['id'])])
                        check_target_record_unlink = odoo_dest.odoo.env['ir.model.data'].browse(check_target_record_unlink)
                        print('Delete #', existing_id, check_target_record_unlink)
                        check_target_record_unlink.unlink()
                        existing_id = False

                print('existing_id', existing_id)
                # res_id = existing_id
                # if processed_record.get('attribute_line_ids'):
                #     continue
                if existing_id \
                        and target_model == 'product.template' \
                        and not processed_record.get('attribute_line_ids') \
                        and processed_record.get('product_variant_id'):
                    # print('product.template', processed_record["product_variant_id"])
                    model_data_id = odoo_dest.search_and_read('ir.model.data',
                                                              [('name', '=',
                                                                f'source_product_product_{processed_record["product_variant_id"]}')],
                                                              ['res_id']
                                                              )
                    if not model_data_id:
                        tmpl_id = odoo_dest.search_and_read(
                            'product.template',
                            [('id', '=', existing_id[0]['res_id'])],
                            ['res_id', 'product_variant_id']
                        )
                        print('tmpl_id', tmpl_id)
                        if tmpl_id:
                            variant_id = odoo_dest.search_and_read(
                                'ir.model.data',
                                [
                                    ('model', '=', 'product.product'),
                                    ('res_id', '=', tmpl_id[0]["product_variant_id"][0])
                                ],
                                ['res_id']
                            )
                            print('variant_id', variant_id, processed_record)
                            if variant_id:
                                variant_id = odoo_dest.odoo.env['ir.model.data'].browse(variant_id[0]['id'])
                                variant_id.unlink()
                            processed_product_variant_id = isinstance(processed_record["product_variant_id"], int) and \
                                                           processed_record["product_variant_id"] or \
                                                           processed_record["product_variant_id"][0]
                            odoo_dest.odoo.env['ir.model.data'].create({
                                'name': f'source_product_product_{processed_product_variant_id}',
                                'model': 'product.product',
                                'module': 'remote_multi_company',
                                'res_id': tmpl_id[0]["product_variant_id"][0],
                            })
                    # continue
                if existing_id and MODEL == 'stock.move':
                    del processed_record['product_uom']

                if TARGET_MODEL == 'product.template.attribute.line':
                    model_data_id = odoo_dest.search_and_read('product.template.attribute.line',
                                                              [
                                                                  ('product_tmpl_id', '=', processed_record['product_tmpl_id']),
                                                                  ('attribute_id', '=', processed_record['attribute_id'])
                                                               ],
                                                              ['product_tmpl_id', 'attribute_id', 'value_ids']
                                                              )
                    if model_data_id:
                        existing_id = model_data_id
                        if len(set(processed_record['value_ids']).intersection(processed_record['value_ids'])) == len(model_data_id[0]['value_ids']):
                            BLOCKED_FIELDS.append(processed_record['attribute_id'])
                            print("Skip #", display_processed_record(processed_record), list(set(processed_record['value_ids']).intersection(model_data_id[0]['value_ids'])))
                            continue
                        else:
                            print('product.template.attribute.line #', existing_id, list(set(processed_record['value_ids']).intersection(model_data_id[0]['value_ids'])), processed_record['attribute_id'])

                if TARGET_MODEL == 'product.set.pricelist':
                    product_set_pricelist = odoo_dest.search_and_read(
                        'product.set.pricelist',
                        [
                            ('product_set_id', '=', processed_record['product_set_id']),
                            ('pricelist_id', '=', processed_record['pricelist_id']),
                            ('company_id', '=', processed_record['company_id']),
                            ('currency_id', '=', processed_record['currency_id'])
                        ],
                        ['product_set_id', 'pricelist_id', 'company_id', 'currency_id'])
                    print('product_set_pricelist', product_set_pricelist)
                    if product_set_pricelist:
                        print("Skip #", display_processed_record(processed_record))
                        continue

                if MODEL == 'purchase.order':
                    picking_type = odoo_dest.search_and_read(
                        'stock.picking.type',
                        [
                            ('code', '=', 'incoming'),
                            ('warehouse_id.company_id', '=', processed_record['company_id'])],
                        ['name'])
                    if not picking_type:
                        picking_type = odoo_dest.search_and_read(
                            'stock.picking.type',
                            [
                                ('code', '=', 'incoming'),
                                ('warehouse_id', '=', False)
                            ], ['name'])
                    print('picking_type_id #', picking_type)
                    if picking_type:
                        processed_record['picking_type_id'] = picking_type[0]['id']
                    else:
                        print("Skip #", {k: v for k, v in processed_record.items() if k not in ['datas', 'image', 'image_1920']})
                        continue

                if existing_id:
                    for field_exeption in EXCEPTION_FIELDS:
                        del processed_record[field_exeption]

                print('Record to save #:',
                      display_processed_record(processed_record),
                      target_model)
                counter += 1
                if existing_id:
                    res_id = existing_id[0].get('res_id') or existing_id[0].get('id')
                    # Update existing record
                    odoo_dest.odoo.env[target_model].write(res_id, processed_record)
                else:
                    # Create new record with external_id set
                    res_id = odoo_dest.odoo.env[target_model].create(processed_record)
                    # if TARGET_MODEL != 'product.set.pricelist':
                    odoo_dest.odoo.env['ir.model.data'].create({
                        'name': f'source_{MODEL.replace(".", "_")}_{record["id"]}',
                        'model': target_model,
                        'module': 'remote_multi_company',
                        'res_id': res_id,
                    })
                    # res_id = new_id
                # if target_model == 'product.manufacturer.datasheets' and odoo_dest.path and processed_record[
                #     'store_fname']:
                #     folder, file_name = processed_record['store_fname'].split('/')
                #     src_file = os.path.join(odoo_src.path, folder, file_name)
                #     dst_folder = os.path.join(odoo_dest.path, folder)
                #     shutil.copy2(src_file, dst_folder)

                # print(f'{res_id}', end="\r", flush=True)
    # blocked_fields = list(filter(lambda r: r is not None, BLOCKED_FIELDS))
    # if blocked_fields:
    #     print("Blocked #:\n", "\n".join(blocked_fields))
    print("Skipped #:", skips_ids)
    print("Counter #:", counter)
    print("Unique ids:", FIELD_ID_MAPPING_SAVE)
    print("Last record #", os.environ.get('CURRENT_ROW'))

def process_step_mode_2(step):
    # Load configuration from file
    if not COMPARE_FILED:
        return
    last_id = 0
    start = True
    header = ['id', 'name', 'default_code']
    skips_ids = []
    product_ids = []
    if MODEL == 'res.partner':
        source_parent_ids = odoo_src.search_and_read('res.company', [], ['partner_id'], order='id')
        print('Skip company ids', source_parent_ids)
        parent_ids = [x['partner_id'][0] for x in source_parent_ids]
        child_ids = odoo_src.search_and_read('res.partner', [('parent_id', 'in', parent_ids)], [], order='id')
        parent_ids += [x['id'] for x in child_ids]
    elif MODEL in ('product.category', 'product.product', 'product.uom.categ'):
        source_parent_ids = odoo_src.search_and_read('ir.model.data',
                                                     [('module', '!=', '__export__'), ('module', '!=', 'remote_multi_company'), ('model', '=', MODEL)],
                                                     ['res_id'], order='id')
        parent_ids = [x['res_id'] for x in source_parent_ids]
    else:
        parent_ids = False

    for search_domain in SEARCH_DOMAINS:
        wrong_product_tmpl_id = {}
        while start:
            if parent_ids:
                search_domain += [('id', 'not in', parent_ids)]
            print(['Search domain', ('id', '>', last_id)] + SEARCH_DOMAIN + search_domain)
            # Fetch data from source
            source_data = odoo_src.search_and_read(MODEL, [('id', '>', last_id)] + SEARCH_DOMAIN + search_domain,
                                                   FIELDS, limit=1000, order=ORDER)
            if not source_data:
                start = False
                break
            # Process and import/update in destination
            for record in source_data:
                target_id = False
                # _logger.info(f"{record}:{wrong_product_tmpl_id}")
                if record.get('product_tmpl_id') and not wrong_product_tmpl_id.get(record['product_tmpl_id'][0]):
                    wrong_product_tmpl_id[record['product_tmpl_id'][0]] = {}
                if record.get('attribute_value_ids'):
                    if not wrong_product_tmpl_id[record['product_tmpl_id'][0]].get(
                            "-".join(map(str, set(record['attribute_value_ids'])))):
                        wrong_product_tmpl_id[record['product_tmpl_id'][0]][
                            "-".join(map(str, set(record['attribute_value_ids'])))] = []
                    wrong_product_tmpl_id[record['product_tmpl_id'][0]][
                        "-".join(map(str, set(record['attribute_value_ids'])))].append(record["id"])

                last_id = record['id']
                target_model = TARGET_MODEL or MODEL
                # Search for existing external_id in the destination database
                existing_id = odoo_dest.search_and_read('ir.model.data',
                                                        [
                                                            ('name', '=',
                                                             f'source_{MODEL.replace(".", "_")}_{record["id"]}'),
                                                            ('model', '=', target_model)
                                                        ],
                                                        ['res_id'])
                if record.get('default_code') and not existing_id:
                    target_id = odoo_dest.search_and_read(target_model,
                                                          [(COMPARE_FILED, '=', record[COMPARE_FILED])],
                                                          [COMPARE_FILED]
                                                          )
                    if target_id:
                        odoo_dest.odoo.env['ir.model.data'].create({
                            'name': f'source_{MODEL.replace(".", "_")}_{record["id"]}',
                            'model': target_model,
                            'module': 'remote_multi_company',
                            'res_id': target_id[0]['id'],
                        })
                    else:
                        skips_ids.append({
                            'id': record['id'],
                            'name': record['name'],
                            'default_code': record['default_code'],
                        })
                print('row', f"{existing_id == [] and not target_id and 'NOT' or 'OK'}", ": ", record)

        for key, values in wrong_product_tmpl_id.items():
            for product_set, product_id in values.items():
                if len(product_id) > 1:
                    for wrong_product in product_id:
                        source_data = odoo_src.search_and_read(MODEL,
                                                               [('id', '=', wrong_product)],
                                                               FIELDS, order=ORDER)
                        for wrong_product_id in source_data:
                            product_ids.append({
                                'id': wrong_product_id['id'],
                                'name': wrong_product_id['name'],
                                'default_code': wrong_product_id['default_code'],
                            })

    with open('/tmp/errors.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(skips_ids)
    with open('/tmp/product_errors.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(product_ids)

        # Process and import/update in destination


if __name__ == '__main__':
    file_name = len(sys.argv) > 1 and sys.argv[1] or "odoo2odoo.ini"
    print(f"argv: {sys.argv[0]} {file_name}")
    print(glob.glob("/etc/odoo/conf/*"))
    with open(file_name) as f:
        print(f.read())

    if not os.path.exists(file_name):
        print('Please use command: import_model_odoorpc_steps_v_2_11.py [file name]')
        exit(1)
    config = configparser.ConfigParser()
    config.read(file_name, "utf-8")

    # Create Odoo client instances for source and destination
    odoo_src = OdooClient(config["OdooSource"])
    VERSION_SRC = int(odoo_src.odoo.version.split(".")[0])

    odoo_dest = OdooClient(config["OdooDestination"])
    odoo_dest.set_environment({'no_vat_validation': True})
    VERSION_DEST = int(odoo_dest.odoo.version.split(".")[0])

    for step in EXECUTE:
        print("Starting step", f'step_{step}', STEPS[f'step_{step}'])
        MODEL = STEPS[f'step_{step}']['MODEL']
        TARGET_MODEL = STEPS[f'step_{step}']['TARGET_MODEL']
        SEARCH_DOMAIN = STEPS[f'step_{step}']['SEARCH_DOMAIN']
        SEARCH_DOMAINS = STEPS[f'step_{step}']['SEARCH_DOMAINS']

        FIELDS = STEPS[f'step_{step}']['FIELDS']
        SKIP_FIELDS = STEPS[f'step_{step}']['SKIP_FIELDS']
        RELATIONAL_FIELDS = STEPS[f'step_{step}']['RELATIONAL_FIELDS']
        FIELD_MAPPING = STEPS[f'step_{step}']['FIELD_MAPPING']
        FIELD_ID_MAPPING = STEPS[f'step_{step}'].get('FIELD_ID_MAPPING', {})
        ORDER = STEPS[f'step_{step}']['ORDER']
        COMPARE_FILED = STEPS[f'step_{step}']['COMPARE_FILED']

        PRODUCT_CATEGORY = STEPS[f'step_{step}'].get('PRODUCT_CATEGORY') or []
        DEFAULT_FIELDS = STEPS[f'step_{step}'].get('DEFAULT_FIELDS') or {}

        EXCEPTION_FIELDS = STEPS[f'step_{step}'].get('EXCEPTION_FIELDS') or []
        ACTION = STEPS[f'step_{step}'].get('ACTION') or False

        if GLOBAL_MODE == 1:
            process_step_mode_1(step)
        elif GLOBAL_MODE == 2:
            process_step_mode_2(step)
