from default_parsers import parse_comma_list, UserInputException


def parse_catalog_type(catalog_type : str):
    options = {
        'dc':'DC Wholesale Pricing Catalog',
        'customer':'Customer Specific Pricing Catalog'
    }
    if catalog_type not in options:
        raise UserInputException(f"Param <catalog_type> must be one of {list(options.keys())}") 
    return options[catalog_type]


# item_group=master
def parse_item_group(item_group : str):
    options = {
        'master':'Item Master', 
        'authorized':'Authorized List', 
        'current':'Current Orders', 
        'history':'Item History'#, 
        # 'order':'Order Type'
    }

    if item_group not in options:
        raise UserInputException(f"Param <item_group> must be one of {list(options.keys())}, given {item_group}")
    # elif item_group == 'order':
    #     raise UserInputException(f"Item group option 'order' not yet supported")
    return options[item_group]


def parse_kehe_format(_format : str):
    formats = parse_comma_list(_format)
    options = ['xls', 'csv', 'txt']
    new_formats = []
    for format in formats:
        if format not in options:
            raise UserInputException(f"Each format in list of formats must be one of {options}, given <{format}>")
        w_period = "." + format
        new_formats.append(w_period)
    return new_formats


# acct=17201
def parse_kehe_acct(acct : str):
    if acct not in ['172011', '049698']:
        raise UserInputException(f'Account number "{acct}" not recognized, must be one of 172011 or 049698')
    return acct