from default_parsers import *
from params import *


# Assign parameters to their respective parsing functions
default_parser_dict = {
    ACCT:parse_acct, FORMAT:parse_comma_list, NOTIFYGET:parse_string, NOTIFYFILE:parse_string, 
    LOG:parse_string, LOGLEVEL:parse_loglevel, START : parse_startdate, END : parse_enddate, 
    # Only for catalogues
    PERIOD:parse_period,
    TYPE:parse_comma_list,
    THROTTLE:parse_throttle,
    # Only for invoices

    # Server params
    SUPPLIER:parse_supplier,
    ENTITY_TYPE:parse_entity_type
}


# Pass sys.argv as argument
def parse_keyvals(argv) -> dict:
    """
    Given argv which looks like  ['script.py', 'arg_foo=thing1', 'arg_bar=thing2']
    
    Returns dict  {arg_foo:"thing1", arg_bar:"thing2"}, where values are unprocessed raw strings
    
    Enforces a non-empty value for each key
    """
    if type(argv) == dict:
        return argv

    if len(argv) == 0:
        raise UserInputException("No parameters were provided")
    
    # Remove first element of argv (name of the calling script)
    argv.pop(0) 
    
    arg_dict = dict({})
    for arg in argv:
        key_value = arg.split("=")
        
        if len(key_value) > 2:
            raise UserInputException(f"More than one \"=\" detected in given parameter <{arg}>")
        elif len(key_value) < 2:
            raise UserInputException(f'No value given for parameter <{key_value[0]}>')
        elif not key_value[1]:
            raise UserInputException(f'Empty value given for parameter <{key_value[0]}>')
            
        key, value = (key_value[0], key_value[1])
        arg_dict[key] = value
    return arg_dict


def parse_values(arg_dict, parser_dict=default_parser_dict):
    """
    This is what the download script(s) use to re-format values of parameters into
    data structures that Python understands, using the parser functions above.
    
    Given argv, process each of the parameters' values, 
    according to the parsers specified for each parameter in the given parser dictionary.
    """
    for key in arg_dict.keys():
        try:
            parser = parser_dict[key]
        except KeyError:
            raise UserInputException(f"Unrecognized / unsupported parameter <{key}>: no parser was applied to this parameter")
        # Apply respective handler to each parameter's value
        arg_dict[key] = parser(arg_dict[key])

    return arg_dict