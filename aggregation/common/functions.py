def get_choices_value(field, choices):
    value = dict(choices).get(field)
    if not value:
        return {y: x for x, y in choices}.get(field)
    return value
