# [5] product.attribute.value
def _get_product_attribute_value():
    return {
        'MODEL': 'product.attribute.value',
        'TARGET_MODEL': '',
        'SEARCH_DOMAIN': [],
        'SEARCH_DOMAINS': [[('name', '!=', False)]],
        'FIELDS': ['name', 'sequence', 'attribute_id'],
        'SKIP_FIELDS': [],
        'RELATIONAL_FIELDS': ['attribute_id'],
        'FIELD_MAPPING': {},
        'ORDER': 'id',
        'COMPARE_FILED': '',
    }
