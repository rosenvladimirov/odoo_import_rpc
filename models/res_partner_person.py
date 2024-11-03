# [2] persons in res.partner
# 'FIELDS': ['name', 'email', 'address', 'vat', 'type', 'parent_id', 'company_type', 'lang',
#                              'country_id', 'street', 'street2',
#                              'city', 'zip', 'phone', 'mobile', "image"]
def _get_res_partner_person():
    return {
        'MODEL': 'res.partner',  # Example model
        'TARGET_MODEL': '',
        'SEARCH_DOMAIN': [],
        'SEARCH_DOMAINS': [[('parent_id', '!=', False)]],
        'AUTO': True,
        'SKIP_FIELDS': [],
        'RELATIONAL_FIELDS': ['parent_id', 'country_id'],
        'FIELD_MAPPING': {
            'image': 'image_1920',
            # 'uid': 'l10n_bg_uic',
        },
        'ORDER': 'id',
        'COMPARE_FILED': 'ref',
        # 'DEFAULT_FIELDS': {'company_id': 2},
    }