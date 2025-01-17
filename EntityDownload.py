import parsing
from params import *
from default_parsers import UserInputException, parse_log, parse_loglevel, parse_notifyfile
from datetime import date

from date_range_helpers import convert_to_date

class EntityDownload():
    """
    Standard flow:
    entity_download = EntityDownload(sys.argv, additional_parsers, defaults)
    ...
    entity_download.process_files() # asserts writability of log/notify files, process their params too
    entity_download.process_params() # process the rest of the params
    ...
    # Use entity_download.param_dict to access key/val pairs, where vals were parsed using default and provided parsers
    # e.g.
    entity_download.param_dict[params.LOG]  # 'mylog.txt'

    
    Enables efficient parameter processing/initialization for any class which is used to 
    download any entity. Requires argv and a dictionary whose keys are (additional) parameters
    which are unique to the inheriting class, and whose values are the respective functions
    designed to parse the parameters' values/arguments given at the command line.

    * This dictionary can be created using preexistent parser functions defined in the 
      <default_parsers> module. 
    * Custom functions are of course required for parameters
      which cannot be parsed using any of the preexistent ones.

    After the initialization process is complete, the following class attributes
    will possess the qualiti(es) which describe them below.
    
    Attributes:
    parser_dict       :  dictionary which maps each supported parameter
                         to its corresponding parser function

    param_dict        :  dictionary which maps parameters to the values parsed on the command line

    argv              :  provided argv (list of arguments given on command line)
    """
    # python script.py type=regular acct=1234
    # argv looks like ['script.py', 'type=regular', 'acct=1234']
    def __init__(self, argv, additional_parsers_dict=dict({}), default_values=dict({}) ):
        self.argv = argv
        self.parser_dict = parsing.default_parser_dict  # {ACCT: parse_acct, .....}
        self.update_parser_dict(additional_parsers_dict)

        # Establish default values
        self.param_dict = {
            START:0,
            END:30,
            TYPE:[REGULAR],
            LOG:'/dev/null',
            LOGLEVEL:'warning'
        }

        self.set_default_values(default_values)


    def print_param_dict(self):
        param_pretty = '[['
        for param_name in self.param_dict:
            param_pretty += f"'{param_name}' : {str(self.param_dict[param_name])}, "
        param_pretty = param_pretty[:-2]
        param_pretty += ']]'
        print(param_pretty) if len(param_pretty) > 2 else print('Empty param dict')


    def process_files(self):
        self.raw_arg_dict = parsing.parse_keyvals(self.argv)
        if LOG        in self.raw_arg_dict.keys():
            self.param_dict[LOG]        = parse_log(self.raw_arg_dict[LOG])
        if LOGLEVEL   in self.raw_arg_dict.keys():
            self.param_dict[LOGLEVEL]   = parse_loglevel(self.raw_arg_dict[LOGLEVEL])
        if NOTIFYFILE in self.raw_arg_dict.keys():
            self.param_dict[NOTIFYFILE] = parse_notifyfile(self.raw_arg_dict[NOTIFYFILE])


    def process_params(self):
        if not hasattr(self, 'raw_arg_dict'):
            raise Exception('process_params() cannot be run without first running process_files()')
        
        clean_parsed_dict = parsing.parse_values(self.raw_arg_dict, self.parser_dict)
        for param in clean_parsed_dict.keys():
            self.param_dict[param] = clean_parsed_dict[param]
        self.convert_dates()
        self.validate_date_range()


    def convert_dates(self):
        self.param_dict[START] = convert_to_date(self.param_dict[START])
        self.param_dict[END]   = convert_to_date(self.param_dict[END])


    def validate_date_range(self):
        _start = self.param_dict[START]
        _end   = self.param_dict[END]
        # Convert to date objects in case they were not before
        start = date(_start.year, _start.month, _start.day)
        end   = date(_end.year,   _end.month,   _end.day  )
        if (end - start).days < 0:
            raise UserInputException('Provided end date comes before start date')


    def set_default_values(self, default_values):
        for param in default_values.keys():
            self.param_dict[param] = default_values[param]


    def update_parser_dict(self, additional):
        for param in additional.keys():
            self.parser_dict[param] = additional[param]
        

    


# add = {'foo':parse_int}
# def main():
#     ed = EntityDownload(sys.argv, add)
#     print(ed.param_dict)
# main()