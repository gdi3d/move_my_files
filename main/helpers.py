from datetime import datetime

def filename_pattern_transform(value):

    today = datetime.today()

    if '%' in value:
        return today.strftime(value)
    else:
        return value
