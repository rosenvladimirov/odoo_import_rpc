import os
import sys

import odoorpc
import configparser
import logging
import shutil

logging.basicConfig()
_logger = logging.getLogger('odoorpc')
_logger.setLevel(logging.INFO)

GLOBAL_SKIP = False
GLOBAL_MODE = 1  # 1 - normal, 2 - only link database
RPC_LANG = 'en_US'  # bg_BG, el_GR, en_US
STEPS = {'step_1': {}, 'step_2': {}, 'step_3': {}, 'step_4': {}, 'step_5': {}, 'step_6': {}, 'step_7': {}, 'step_8': {},
         'step_9': {}, 'step_10': {}, 'step_11': {}, 'step_12': {}, 'step_13': {}, 'step_14': {}, 'step_15': {},
         'step_16': {}, 'step_17': {}, 'step_18': {}, 'step_19': {}, 'step_20': {}, 'step_21': {}, 'step_22': {},
         'step_23': {}, 'step_24': {}, 'step_25': {}, 'step_26': {}, 'step_27': {}}
EXECUTE = [9]

# [1] res.partner
STEPS['step_1']['MODEL'] = 'res.partner'  # Example model
STEPS['step_1']['TARGET_MODEL'] = ''
STEPS['step_1']['SEARCH_DOMAIN'] = [('id', 'not in', [3311, 3492, 3567])]
STEPS['step_1']['SEARCH_DOMAINS'] = [[('parent_id', '=', False)], [('parent_id', '!=', False)]]
STEPS['step_1']['FIELDS'] = ['name', 'email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
                             'display_name_en', 'country_id',
                             'display_name_bg', 'display_name_el', 'country_id', 'street', 'street2',
                             'city', 'zip', 'phone', 'mobile', "image", "uid", ]  # 'image', Example fields
STEPS['step_1']['SKIP_FIELDS'] = ['email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
                                  'display_name_en', 'display_name_bg', 'display_name_el', 'country_id',
                                  'street', 'street2', 'city', 'zip', 'phone', 'mobile', "image", "vat", "uid", ]
STEPS['step_1']['RELATIONAL_FIELDS'] = ['parent_id', 'country_id']  # Add other relational fields as needed
STEPS['step_1']['FIELD_MAPPING'] = {
    # 'image': 'image_1920',
    # 'uid': 'l10n_bg_uic',
}
STEPS['step_1']['ORDER'] = 'id'
STEPS['step_1']['COMPARE_FILED'] = 'vat'

# [2] persons in res.partner
STEPS['step_2']['MODEL'] = 'res.partner'  # Example model
STEPS['step_2']['TARGET_MODEL'] = ''
STEPS['step_2']['SEARCH_DOMAIN'] = [('id', 'not in', [10])]
STEPS['step_2']['SEARCH_DOMAINS'] = [[('parent_id', '!=', False)]]
STEPS['step_2']['FIELDS'] = ['name', 'email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
                             'display_name_en',
                             'display_name_bg', 'display_name_el', 'country_id', 'street', 'street2',
                             'city', 'zip', 'phone', 'mobile', "image", "vat", "uid", ]
STEPS['step_2']['SKIP_FIELDS'] = ['email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
                                  'display_name_en', 'display_name_bg', 'display_name_el', 'country_id', 'street',
                                  'street2', 'city', 'zip', 'phone', 'mobile', "image", "vat", "uid", ]
STEPS['step_2']['RELATIONAL_FIELDS'] = ['parent_id', 'country_id']
STEPS['step_2']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    'uid': 'l10n_bg_uic',
}
STEPS['step_2']['ORDER'] = 'id'
STEPS['step_2']['COMPARE_FILED'] = ''

# [3] product.category
STEPS['step_3']['MODEL'] = 'product.category'  # Example model
STEPS['step_3']['TARGET_MODEL'] = ''
STEPS['step_3']['SEARCH_DOMAIN'] = [('id', 'in', [277, 458])]
STEPS['step_3']['SEARCH_DOMAINS'] = [[('parent_id', '!=', False)]]
STEPS['step_3']['FIELDS'] = ['name', 'parent_id', 'complete_name']
STEPS['step_3']['SKIP_FIELDS'] = ['parent_id']
STEPS['step_3']['RELATIONAL_FIELDS'] = ['parent_id']
STEPS['step_3']['FIELD_MAPPING'] = {}
STEPS['step_3']['ORDER'] = 'parent_left'
STEPS['step_3']['COMPARE_FILED'] = 'complete_name'

# [4] product attribute
STEPS['step_4']['MODEL'] = 'product.attribute'  # Example model
STEPS['step_4']['TARGET_MODEL'] = ''
STEPS['step_4']['SEARCH_DOMAIN'] = []
STEPS['step_4']['SEARCH_DOMAINS'] = [[('name', '!=', False)]]
STEPS['step_4']['FIELDS'] = ['name', 'parent_id', 'complete_name']
STEPS['step_4']['SKIP_FIELDS'] = ['parent_id']
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
STEPS['step_5']['SKIP_FIELDS'] = ['sequence', 'attribute_id']
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
STEPS['step_7']['SKIP_FIELDS'] = ['factor', 'uom_type', 'rounding']
STEPS['step_7']['RELATIONAL_FIELDS'] = ['category_id']
STEPS['step_7']['FIELD_MAPPING'] = {}
STEPS['step_7']['ORDER'] = 'id'
STEPS['step_7']['COMPARE_FILED'] = ''

# [8] product.template
STEPS['step_8']['MODEL'] = 'product.template'
STEPS['step_8']['TARGET_MODEL'] = ''
STEPS['step_8']['SEARCH_DOMAIN'] = [('attribute_line_ids', '=', False)]
STEPS['step_8']['SEARCH_DOMAINS'] = [[('active', '=', True)]]
STEPS['step_8']['FIELDS'] = ['name', 'sequence', 'description', 'description_purchase', 'description_sale', 'description_short',
                             'type', 'currency_id', 'list_price', 'standard_price', 'image',
                             'volume', 'weight', 'sale_ok', 'purchase_ok', 'uom_id', 'uom_po_id', 'active',
                             'default_code', 'categ_id', 'product_variant_id']
# STEPS['step_8']['FIELDS'] = ['name', 'description_short', 'sequence', 'description', 'description_purchase', 'description_sale',
#                              'default_code', 'categ_id', 'image', 'attribute_line_ids', 'product_variant_id']
# STEPS['step_8']['FIELDS'] = ['categ_id', 'attribute_line_ids', 'product_variant_id', 'name']
STEPS['step_8']['SKIP_FIELDS'] = ['image', 'manufacturer_id', ]
STEPS['step_8']['RELATIONAL_FIELDS'] = ['parent_id', 'currency_id', 'uom_id', 'uom_po_id', 'attribute_line_ids',
                                        'categ_id', 'product_variant_id']
STEPS['step_8']['FIELD_MAPPING'] = {
    'image': 'image_1920',
}
STEPS['step_8']['ORDER'] = 'id'
STEPS['step_8']['COMPARE_FILED'] = 'default_code'

# [9] product.attribute.line to product.template.attribute.line
STEPS['step_9']['MODEL'] = 'product.attribute.line'
STEPS['step_9']['TARGET_MODEL'] = 'product.template.attribute.line'
STEPS['step_9']['SEARCH_DOMAIN'] = [('product_tmpl_id', 'not in', [118934, 118932])]
STEPS['step_9']['SEARCH_DOMAINS'] = [[('product_tmpl_id.active', '!=', False)]]
STEPS['step_9']['FIELDS'] = ['product_tmpl_id', 'attribute_id', 'value_ids']
STEPS['step_9']['SKIP_FIELDS'] = []
STEPS['step_9']['RELATIONAL_FIELDS'] = ['product_tmpl_id', 'attribute_id', 'value_ids']
STEPS['step_9']['FIELD_MAPPING'] = {}
STEPS['step_9']['ORDER'] = 'id desc'
STEPS['step_9']['COMPARE_FILED'] = ''

# [10] product.product
STEPS['step_10']['MODEL'] = 'product.product'
STEPS['step_10']['TARGET_MODEL'] = ''
STEPS['step_10']['SEARCH_DOMAIN'] = []
STEPS['step_10']['SEARCH_DOMAINS'] = [[('active', '=', True), ('attribute_value_ids', '!=', False)]]
STEPS['step_10']['FIELDS'] = ['name', 'product_tmpl_id', 'active', 'standard_price', 'volume', 'weight',
                              'default_code', 'barcode', 'image', 'attribute_value_ids']
STEPS['step_10']['SKIP_FIELDS'] = ['product_tmpl_id', 'active', 'standard_price', 'volume', 'weight',
                                   'default_code', 'barcode', 'attribute_value_ids']
STEPS['step_10']['RELATIONAL_FIELDS'] = ['product_template_attribute_value_ids']
STEPS['step_10']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    'attribute_value_ids': 'product_template_attribute_value_ids',
}
STEPS['step_10']['ORDER'] = 'id'
STEPS['step_10']['COMPARE_FILED'] = 'default_code'

# [11] product.attribute.value to product.template.attribute.value do not add for execution
STEPS['step_11']['MODEL'] = 'product.attribute.value'
STEPS['step_11']['TARGET_MODEL'] = 'product.template.attribute.value'
STEPS['step_11']['SEARCH_DOMAIN'] = []
STEPS['step_11']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_11']['FIELDS'] = ['name', 'attribute_id', 'product_ids', 'price_extra']
STEPS['step_11']['SKIP_FIELDS'] = ['attribute_id', 'product_ids', 'price_extra']
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
STEPS['step_12']['SKIP_FIELDS'] = ['sequence', 'code', 'field_name']
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
STEPS['step_15']['SKIP_FIELDS'] = ['code', 'image', 'partner_id']
STEPS['step_15']['RELATIONAL_FIELDS'] = ['partner_id', 'company_id']
STEPS['step_15']['FIELD_MAPPING'] = {
    'image': 'image_1920',
    'code': 'ref',
}
STEPS['step_15']['ORDER'] = 'id'
STEPS['step_15']['COMPARE_FILED'] = 'code'

# [15] 	product.set
STEPS['step_25']['MODEL'] = 'product.set'
STEPS['step_25']['TARGET_MODEL'] = ''
STEPS['step_25']['SEARCH_DOMAIN'] = []
STEPS['step_25']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_25']['FIELDS'] = ['name']
STEPS['step_25']['SKIP_FIELDS'] = ['code', 'image', 'partner_id']
STEPS['step_25']['RELATIONAL_FIELDS'] = []
STEPS['step_25']['FIELD_MAPPING'] = {
}
STEPS['step_25']['ORDER'] = 'id'
STEPS['step_25']['COMPARE_FILED'] = 'code'

# [16] 	product.set.line
STEPS['step_16']['MODEL'] = 'product.set.line'
STEPS['step_16']['TARGET_MODEL'] = ''
STEPS['step_16']['SEARCH_DOMAIN'] = [('product_tmpl_id', '!=', 110730)]
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
STEPS['step_17']['SEARCH_DOMAIN'] = [('company_id', '=', 1)]
STEPS['step_17']['SEARCH_DOMAINS'] = [[('active', '!=', False)]]
STEPS['step_17']['FIELDS'] = ['name', 'sequence', 'currency_id', 'company_id', 'discount_policy']
STEPS['step_17']['SKIP_FIELDS'] = ['sequence', 'currency_id', 'company_id', 'discount_policy']
STEPS['step_17']['RELATIONAL_FIELDS'] = ['currency_id', 'company_id']
STEPS['step_17']['FIELD_MAPPING'] = {
}
STEPS['step_17']['ORDER'] = 'id'
STEPS['step_17']['COMPARE_FILED'] = ''

# [18] 	product.pricelist.item
STEPS['step_18']['MODEL'] = 'product.pricelist.item'
STEPS['step_18']['TARGET_MODEL'] = ''
STEPS['step_18']['SEARCH_DOMAIN'] = [('pricelist_id', '=', 36)]
STEPS['step_18']['SEARCH_DOMAINS'] = [[('active', '!=', False)]]
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

# [19] 	sale.order
STEPS['step_19']['MODEL'] = 'sale.order'
STEPS['step_19']['TARGET_MODEL'] = ''
STEPS['step_19']['SEARCH_DOMAIN'] = []
STEPS['step_19']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_19']['FIELDS'] = ['name', 'date_order', 'partner_id', 'partner_contact_id', 'partner_invoice_id',
                              'partner_shipping_id', '', 'company_id', 'validity_date', 'create_date',
                              'pricelist_id',
                              'currency_id', 'amount_untaxed', 'amount_tax', 'amount_total']
STEPS['step_19']['SKIP_FIELDS'] = ['partner_id', 'partner_contact_id', 'partner_invoice_id',
                                   'partner_shipping_id', '', 'company_id', 'validity_date', 'create_date',
                                   'pricelist_id',
                                   'currency_id', 'amount_untaxed', 'amount_tax', 'amount_total']
STEPS['step_19']['RELATIONAL_FIELDS'] = ['partner_id', 'partner_contact_id', 'partner_doctor_id', 'partner_invoice_id',
                                         'partner_shipping_id', 'currency_id', 'company_id', 'pricelist_id']
STEPS['step_19']['FIELD_MAPPING'] = {
    'partner_contact_id': 'partner_doctor_id',
}
STEPS['step_19']['ORDER'] = 'id'
STEPS['step_19']['COMPARE_FILED'] = ''

# [20] 	sale.order.line
STEPS['step_20']['MODEL'] = 'sale.order.line'
STEPS['step_20']['TARGET_MODEL'] = ''
STEPS['step_20']['SEARCH_DOMAIN'] = []
STEPS['step_20']['SEARCH_DOMAINS'] = [[('active', '!=', False)]]
STEPS['step_20']['FIELDS'] = ['pricelist_id', 'company_id', 'currency_id', 'date_start', 'date_end', 'min_quantity',
                              'applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'base', 'compute_price',
                              'fixed_price', 'percent_price', 'price_discount', 'price_round', 'price_surcharge',
                              'price_min_margin', 'price_max_margin', 'product_set_id']
STEPS['step_20']['SKIP_FIELDS'] = []
STEPS['step_20']['RELATIONAL_FIELDS'] = ['pricelist_id', 'company_id', 'currency_id', 'categ_id', 'product_tmpl_id',
                                         'product_id',
                                         'product_set_id']
STEPS['step_20']['FIELD_MAPPING'] = {
}
STEPS['step_20']['ORDER'] = 'id'
STEPS['step_20']['COMPARE_FILED'] = ''

# [22] 	purchase.order
STEPS['step_22']['MODEL'] = 'purchase.order'
STEPS['step_22']['TARGET_MODEL'] = ''
STEPS['step_22']['SEARCH_DOMAIN'] = []
STEPS['step_22']['SEARCH_DOMAINS'] = [[('date_order', '<=', '2022-12-31 00:00:00')]]
STEPS['step_22']['FIELDS'] = ['name', 'date_order', 'currency_id']
STEPS['step_22']['CHILD_FIELDS'] = ['product_id', 'date_order', 'currency_id']
STEPS['step_22']['SKIP_FIELDS'] = []
STEPS['step_22']['RELATIONAL_FIELDS'] = []
STEPS['step_22']['FIELD_MAPPING'] = {
    'partner_contact_id': 'partner_doctor_id',
}
STEPS['step_22']['ORDER'] = 'id'
STEPS['step_22']['COMPARE_FILED'] = ''

# [23] 	purchase.order
STEPS['step_23']['MODEL'] = 'product.manufacturer'
STEPS['step_23']['TARGET_MODEL'] = ''
STEPS['step_23']['SEARCH_DOMAIN'] = [('id', '!=', 143)]
STEPS['step_23']['SEARCH_DOMAINS'] = [[('active', '=', True)]]
STEPS['step_23']['FIELDS'] = ['sequence', 'reelpackaging_ids', 'manufacturer_pname', 'manufacturer_pref',
                              'manufacturer_purl', 'name',
                              'product_tmpl_id', 'product_id']
STEPS['step_23']['CHILD_FIELDS'] = []
STEPS['step_23']['SKIP_FIELDS'] = []
STEPS['step_23']['RELATIONAL_FIELDS'] = ['product_tmpl_id', 'product_id', 'reelpackaging_ids']
STEPS['step_23']['FIELD_MAPPING'] = {
}
STEPS['step_23']['ORDER'] = 'id'
STEPS['step_23']['COMPARE_FILED'] = ''

# [24] 	purchase.order
STEPS['step_24']['MODEL'] = 'product.manufacturer.datasheets'
STEPS['step_24']['TARGET_MODEL'] = ''
STEPS['step_24']['SEARCH_DOMAIN'] = [('manufacturer_id', '!=', 143)]
STEPS['step_24']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_24']['FIELDS'] = ['datas_fname', 'name', 'version', 'manufacturer_id', 'res_model', 'res_id', 'res_name',
                              'store_fname', 'description', 'type', 'mimetype']
STEPS['step_24']['CHILD_FIELDS'] = []
STEPS['step_24']['SKIP_FIELDS'] = []
STEPS['step_24']['RELATIONAL_FIELDS'] = ['manufacturer_id']
STEPS['step_24']['FIELD_MAPPING'] = {
}
STEPS['step_24']['ORDER'] = 'id'
STEPS['step_24']['COMPARE_FILED'] = ''

STEPS['step_27']['MODEL'] = 'product.packaging.type'
STEPS['step_27']['TARGET_MODEL'] = ''
STEPS['step_27']['SEARCH_DOMAIN'] = []
STEPS['step_27']['SEARCH_DOMAINS'] = [[('id', '!=', False)]]
STEPS['step_27']['FIELDS'] = ['categ_id', 'product_tmpl_id', 'product_id', 'product_manufacturer_id', 'name', 'code',
                              'volume_type', 'qty']
STEPS['step_27']['CHILD_FIELDS'] = []
STEPS['step_27']['SKIP_FIELDS'] = []
STEPS['step_27']['RELATIONAL_FIELDS'] = ['categ_id', 'product_tmpl_id', 'product_manufacturer_id', 'product_id']
STEPS['step_27']['FIELD_MAPPING'] = {
}
STEPS['step_27']['ORDER'] = 'id'
STEPS['step_27']['COMPARE_FILED'] = ''

STEPS['step_26']['MODEL'] = 'product.category.packaging.type'
STEPS['step_26']['TARGET_MODEL'] = ''
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


def map_fields(source_record, field_mapping):
    dest_record = {}
    for src_field, value in source_record.items():
        # Map field if it is in the field mapping, otherwise keep the same field name
        dest_field = field_mapping.get(src_field, src_field)
        dest_record[dest_field] = value
    return dest_record


def process_relation_field(relation_record, field_name, relation_model):
    if field_name in relation_record:
        field_value = relation_record[field_name]
        print('Relation #:', field_name, field_value, 'list', isinstance(field_value, list), 'tuple',
              isinstance(field_value, tuple))
        if isinstance(field_value, (list, tuple)) \
                and len(list(filter(str.isdigit, map(str, field_value)))) != len(field_value):
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
                if source_id and source_id[0]['module'] and source_id[0]['module'] != '__export__':
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
                    relation_record[field_name] = field_value[0]
                print(field_name, relation_model, field_value, relation_record[field_name])

            elif field_name in ['partner_id', 'partner_invoice_id', 'partner_shipping_id', 'partner_doctor_id']:
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_res_partner_{field_value[0]}'),
                        ('model', '=', 'res.partner')],
                    ['res_id'])
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                if not parent_id:
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
                    if parent_id:
                        relation_record[field_name] = parent_id[0]['id']
                    else:
                        relation_record['block'] = True
                print('RES Partner', parent_id, field_value, field_name, relation_record[field_name])
            elif field_name in ['product_manufacturer_id', 'manufacturer_id']:
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_manufacturer_{field_value[0]}'),
                        ('model', '=', 'product.manufacturer')],
                    ['res_id'])
                # print(parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True
            elif field_name == 'product_tmpl_id':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_template_{field_value[0]}'),
                        ('model', '=', 'product.template')],
                    ['res_id'])
                # print(parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True
            elif field_name == 'product_id':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_product_{field_value[0]}'),
                        ('model', '=', 'product.product')],
                    ['res_id'])
                print(parent_id, f'source_product_product_{field_value[0]}')
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True

            elif field_name == 'company_id' and field_value[0] != 1:
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_res_company_{field_value[0]}'),
                        ('model', '=', 'res.company')],
                    ['res_id'])
                # print(parent_id, f'source_product_product_{field_value[0]}')
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True
            elif field_name == 'pricelist_id':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_pricelist_{field_value[0]}'),
                        ('model', '=', 'product.pricelist')],
                    ['res_id'])
                print(parent_id, f'source_product_pricelist_{field_value[0]}')
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True

            elif field_name == 'manufacturer_id':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_manufacturer_{field_value[0]}'),
                        ('model', '=', 'product.manufacturer')],
                    ['res_id'])
                print(parent_id, f'source_product_manufacturer_{field_value[0]}')
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True

            elif field_name == 'product_set_id':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_set_{field_value[0]}'),
                        ('model', '=', 'product.set')],
                    ['res_id'])
                print(parent_id, f'source_product_set_{field_value[0]}')
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
                else:
                    relation_record['block'] = True
            elif field_name == 'attribute_id':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_attribute_{field_value[0]}'),
                        ('model', '=', 'product.attribute')],
                    ['res_id'])
                # print(parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
            elif field_name == 'category_id' and MODEL == 'product.uom':
                parent_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_uom_uom_{field_value[0]}'),
                        ('model', '=', 'uom.uom')],
                    ['res_id'])
                # print(parent_id)
                if parent_id:
                    relation_record[field_name] = parent_id[0]['res_id']
            elif field_name == 'categ_id' and relation_model == 'product.template':
                source_id = odoo_src.search_and_read(
                    'ir.model.data',
                    [
                        ('res_id', '=', field_value[0]),
                        ('model', '=', 'product.category')],
                    ['name', 'module'])
                print('Source category', source_id)
                if source_id and source_id[0]['module'] != '__export__':
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
                if source_id and source_id[0]['module'] != '__export__':
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
            elif field_name in ['uom_po_id', 'uom_id']:
                source_id = odoo_src.search_and_read(
                    'ir.model.data',
                    [
                        ('res_id', '=', field_value[0]),
                        ('model', '=', 'product.uom')],
                    ['name', 'module'])
                print('Source uom', source_id)
                if source_id and source_id[0]['module'] != '__export__':
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
                for id_res in field_value:
                    parent_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_template_attribute_line_{id_res}'),
                            ('model', '=', 'product.template.attribute.line')],
                        ['res_id'])
                    if parent_id:
                        ids_parent.append(parent_id[0]['res_id'])
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
                origin_product_tmpl_id = relation_record["product_tmpl_id"]

                product_tmpl_id = odoo_dest.search_and_read(
                    'ir.model.data',
                    [
                        ('name', '=', f'source_product_template_{relation_record["product_tmpl_id"][0]}'),
                        ('model', '=', 'product.template')],
                    ['res_id'])

                if product_tmpl_id:
                    relation_record['product_tmpl_id'] = product_tmpl_id[0]['res_id']

                for id_res in field_value:
                    # origin_product_attribute_line_id = odoo_src.search_and_read(
                    #     'product.attribute.line',
                    #     [
                    #         ('attribute_id', '=', origin_product_attribute_value_id[0]['attribute_id'][0]),
                    #         ('product_tmpl_id', '=', relation_record["product_tmpl_id"][0])
                    #     ],
                    #     ['attribute_id'],
                    #     order='id')
                    # fake line
                    # attribute_line_id = odoo_dest.search_and_read(
                    #     'ir.model.data',
                    #     [
                    #         ('name', '=', f'source_product_template_attribute_line_{origin_product_attribute_line_id[0]["id"]}'),
                    #         ('model', '=', 'product.template.attribute.line')],
                    #     ['res_id'])

                    # get from origin
                    origin_product_attribute_value_id = odoo_src.search_and_read(
                        'product.attribute.value',
                        [
                            ('id', '=', id_res),
                        ],
                        ['name', 'attribute_id'],
                        order='id')
                    # attribute id
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

                    # value id
                    product_attribute_value_id = odoo_dest.search_and_read(
                        'ir.model.data',
                        [
                            ('name', '=', f'source_product_attribute_value_{id_res}'),
                            ('model', '=', 'product.attribute.value'),
                        ],
                        ['res_id'])

                    dest_product_attribute_value_id = odoo_dest.search_and_read(
                        'product.attribute.value',
                        [
                            ('id', '=', product_attribute_value_id[0]['res_id']),
                        ],
                        ['name', 'attribute_id'],
                        order='id')
                    print('\n')
                    print('Attribute filter #:')
                    print('dest_product_attribute_value_id', dest_product_attribute_value_id)
                    print('product_tmpl_id', relation_record["product_tmpl_id"])
                    print('origin_product_tmpl_id', origin_product_tmpl_id)
                    print('origin_product_attribute_value_id', origin_product_attribute_value_id)

                    print('product_attribute_value_id', product_attribute_value_id)
                    print('attribute_id', attribute_id)
                    print('dest_attribute_id', dest_attribute_id)
                    # print('attribute_line_id', attribute_line_id)

                    product_template_attribute_value_id = odoo_dest.search_and_read(
                        'product.template.attribute.value',
                        [
                            ('product_attribute_value_id', '=', product_attribute_value_id[0]['res_id']),
                            ('attribute_id', '=', attribute_id[0]['res_id']),
                            ('product_tmpl_id', '=', relation_record["product_tmpl_id"]),
                        ],
                        ['name'])

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


def process_record(active_model, active_record):
    for field in RELATIONAL_FIELDS:
        process_relation_field(active_record, field, active_model)

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
                ['product_tmpl_id'])
            print(id_product)
            ids_product.update([id_product[0]['product_tmpl_id']])
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


def process_step_mode_1(step):
    # Load configuration from file
    last_id = 0
    start = True
    skips_ids = []
    if MODEL == 'res.partner':
        source_parent_ids = odoo_src.search_and_read('res.company', [], ['partner_id'], order='id')
        print('Skip company ids', source_parent_ids)
        parent_ids = [x['partner_id'][0] for x in source_parent_ids]
        child_ids = odoo_src.search_and_read('res.partner', [('parent_id', 'in', parent_ids)], [], order='id')
        parent_ids += [x['id'] for x in child_ids]
    elif MODEL in ('product.category', 'product.product', 'product.uom.categ'):
        source_parent_ids = odoo_src.search_and_read('ir.model.data',
                                                     [('module', '!=', '__export__'), ('model', '=', MODEL)],
                                                     ['res_id'], order='id')
        parent_ids = [x['res_id'] for x in source_parent_ids]
    else:
        parent_ids = False

    for search_domain in SEARCH_DOMAINS:
        while start:
            if parent_ids:
                search_domain += [('id', 'not in', parent_ids)]
            print(['Search domain', ('id', '>', last_id)] + SEARCH_DOMAIN + search_domain)
            # Fetch data from source
            source_data = odoo_src.search_and_read(MODEL, [('id', '>', last_id)] + SEARCH_DOMAIN + search_domain,
                                                   FIELDS, limit=100, order=ORDER)
            if not source_data:
                start = False
                break
            # Process and import/update in destination
            for record in source_data:
                last_id = record['id']
                if MODEL == 'product.properties.static':
                    if len([f"{k}:{v}" for k, v in record.items() if k not in ['id', 'object_id'] and v]) == 0 \
                            or not record['object_id']:
                        skips_ids.append(record['id'])
                        print("Skip record #:", record['id'])
                        continue

                print('Record #:',
                      TARGET_MODEL or MODEL,
                      [f"{k}:{v}" for k, v in record.items() if k not in ['id', 'object_id', 'image'] and v],
                      f"{record['id']}=>{last_id}")
                mapped_record = map_fields(record, FIELD_MAPPING)  # Pass the field_mapping dictionary here
                processed_record = process_record(MODEL, mapped_record)  # Process the record
                if processed_record.get('block'):
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

                if MODEL == 'product.product':
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
                                                        ['res_id'])
                if not existing_id and COMPARE_FILED and record.get(COMPARE_FILED):
                    target_id = odoo_dest.search_and_read(target_model,
                                                          [(COMPARE_FILED, '=', record[COMPARE_FILED].strip())],
                                                          [COMPARE_FILED]
                                                          )
                    if target_id:
                        model_data_id = odoo_dest.search_and_read('ir.model.data',
                                                                  ('res_id', '=', target_id[0]['id']),
                                                                  ['res_id']
                                                                  )
                        if model_data_id:
                            model_data_id = odoo_dest.odoo.env['ir.model.data'].browse(model_data_id[0]['id'])
                            model_data_id.unlink()
                        odoo_dest.odoo.env['ir.model.data'].create({
                            'name': f'source_{MODEL.replace(".", "_")}_{record["id"]}',
                            'model': target_model,
                            'module': 'remote_multi_company',
                            'res_id': target_id[0]['id'],
                        })
                        # continue
                print('existing_id', existing_id)
                # res_id = existing_id
                print('Record to save #:', {k: v for k, v in processed_record.items() if k != 'datas'}, target_model)
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
                            print('variant_id', variant_id)

                            variant_id = odoo_dest.odoo.env['ir.model.data'].browse(variant_id[0]['id'])
                            if variant_id:
                                variant_id.unlink()
                            odoo_dest.odoo.env['ir.model.data'].create({
                                'name': f'source_product_product_{processed_record["product_variant_id"]}',
                                'model': 'product.product',
                                'module': 'remote_multi_company',
                                'res_id': tmpl_id[0]["product_variant_id"][0],
                            })
                    continue

                if existing_id:
                    res_id = existing_id[0].get('res_id') or existing_id[0].get('id')
                    # Update existing record
                    odoo_dest.odoo.env[target_model].write(res_id, processed_record)
                else:
                    # Create new record with external_id set
                    res_id = odoo_dest.odoo.env[target_model].create(processed_record)
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
    print("Skipped #:", skips_ids)


def process_step_mode_2(step):
    # Load configuration from file
    if not COMPARE_FILED:
        return
    last_id = 0
    start = True
    skips_ids = []
    if MODEL == 'res.partner':
        source_parent_ids = odoo_src.search_and_read('res.company', [], ['partner_id'], order='id')
        print('Skip company ids', source_parent_ids)
        parent_ids = [x['partner_id'][0] for x in source_parent_ids]
        child_ids = odoo_src.search_and_read('res.partner', [('parent_id', 'in', parent_ids)], [], order='id')
        parent_ids += [x['id'] for x in child_ids]
    elif MODEL in ('product.category', 'product.product', 'product.uom.categ'):
        source_parent_ids = odoo_src.search_and_read('ir.model.data',
                                                     [('module', '!=', '__export__'), ('model', '=', MODEL)],
                                                     ['res_id'], order='id')
        parent_ids = [x['res_id'] for x in source_parent_ids]
    else:
        parent_ids = False

    for search_domain in SEARCH_DOMAINS:
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
                if not existing_id:
                    target_id = odoo_dest.search_and_read(target_model,
                                                          [(COMPARE_FILED, '=', record[COMPARE_FILED])],
                                                          [COMPARE_FILED]
                                                          )
                    if not target_id:
                        odoo_dest.odoo.env['ir.model.data'].create({
                            'name': f'source_{MODEL.replace(".", "_")}_{record["id"]}',
                            'model': target_model,
                            'module': 'remote_multi_company',
                            'res_id': target_id[0]['id'],
                        })
                    print('existing_id', existing_id, target_id)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("./main.ini", "utf-8")

    # Create Odoo client instances for source and destination
    odoo_src = OdooClient(config["OdooSource"])
    odoo_dest = OdooClient(config["OdooDestination"])
    odoo_dest.set_environment({'no_vat_validation': True})

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
        ORDER = STEPS[f'step_{step}']['ORDER']
        COMPARE_FILED = STEPS[f'step_{step}']['COMPARE_FILED']
        if GLOBAL_MODE == 1:
            process_step_mode_1(step)
        elif GLOBAL_MODE == 2:
            process_step_mode_2(step)
