# [1] res.partner
# 'FIELDS': ['name', 'email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
#            'country_id', 'country_id', 'street', 'street2',
#            'city', 'zip', 'phone', 'mobile', "image", "company_id", "image"]  # 'image', Example fields
def _get_res_partner():
    return {
        'MODEL': 'res.partner',  # Example model
        'TARGET_MODEL': '',
        'SEARCH_DOMAIN': [('is_company', '=', True)],
        'SEARCH_DOMAINS': [[('parent_id', '=', False)]],
        'AUTO': True,
        # if use auto mode skip this field
        # 'FIELDS': ['name', 'email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
        #                              'country_id', 'country_id', 'street', 'street2',
        #                              'city', 'zip', 'phone', 'mobile', "image", "company_id", "image"],
        'SKIP_FIELDS': [],
        'RELATIONAL_FIELDS': ['parent_id', 'country_id'],  # Add other relational fields as needed
        'FIELD_MAPPING': {
            'image': 'image_1920',
            # 'uid': 'l10n_bg_uic',
        },
        'ORDER': 'id',
        'COMPARE_FILED': 'vat',
        # 'DEFAULT_FIELDS': {'company_id': 2},
    }
