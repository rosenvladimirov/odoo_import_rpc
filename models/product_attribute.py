def _get_product_attribute():
    return {
        'MODEL': 'product.attribute',
        'TARGET_MODEL': '',
        'SEARCH_DOMAIN': [],
        'SEARCH_DOMAINS': [[('name', '!=', False)]],
        'FIELDS': ['name', 'parent_id', 'complete_name'],
        'SKIP_FIELDS': [],
        'RELATIONAL_FIELDS': [],
        'FIELD_MAPPING': {},
        'ORDER': 'id',
        'COMPARE_FILED': '',
    }