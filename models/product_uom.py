# [7] product.uom to uom.uom
def _get_product_uom():
    return {
        'MODEL': 'product.uom',
        'TARGET_MODEL': 'uom.uom',
        'SEARCH_DOMAIN': [],
        'SEARCH_DOMAINS': [[('active', '!=', False)]],
        'FIELDS': ['name', 'factor', 'uom_type', 'rounding'],
        'SKIP_FIELDS': [],
        'RELATIONAL_FIELDS': ['category_id'],
        'FIELD_MAPPING': {},
        'ORDER': 'id',
        'COMPARE_FILED': ''
    }
