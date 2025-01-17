from distutils.util import strtobool

def stringtobool(string : str):
  return not not strtobool(string)