# [3] product.category
def _get_product_category():
    return {
        'MODEL': 'product.category',  # Example model
        'TARGET_MODEL': '',
        'SEARCH_DOMAIN': [],
        'SEARCH_DOMAINS': [[('complete_name', 'like', 'All / Saleable%')]],
        'FIELDS': ['name', 'parent_id', 'complete_name'],
        'SKIP_FIELDS': [],
        'RELATIONAL_FIELDS': ['parent_id'],
        'FIELD_MAPPING': {},
        'ORDER': 'complete_name',
        'COMPARE_FILED': 'complete_name',
    }
