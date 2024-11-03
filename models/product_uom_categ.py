# [6] product.uom.categ to uom.category
def _get_product_uom_categ():
    return {
        'MODEL': 'product.uom.categ',
        'TARGET_MODEL': 'uom.category',
        'SEARCH_DOMAIN': [],
        'SEARCH_DOMAINS': [[('name', '!=', False)]],
        'FIELDS': ['name'],
        'SKIP_FIELDS': [],
        'RELATIONAL_FIELDS': [],
        'FIELD_MAPPING': {},
        'ORDER': 'id',
        'COMPARE_FILED': '',
    }
