import params as p
import parsing
from default_parsers import UserInputException

required_params = {p.SUPPLIER, p.ENTITY_TYPE}

class RequestParser():
    def __init__(self, argv):
        self.argv = argv
        self.parser_dict = parsing.default_parser_dict

        # Establish default values
        self.param_dict = {
            p.LOG:'/dev/null',
            p.LOGLEVEL:'warning'
        }

        self.update_param_dict()
        self.enforce_required_params()

    def update_param_dict(self):
        clean_parsed_dict = parsing.parse_values(self.argv, self.parser_dict)
        for param in clean_parsed_dict.keys():
            self.param_dict[param] = clean_parsed_dict[param]

    
    def enforce_required_params(self):
        missing = []
        for param in required_params:
            if param not in self.param_dict:
                missing.append(param)
        
        if len(missing) > 0:
            raise UserInputException(f'Request lacks required param(s): <{missing}>')