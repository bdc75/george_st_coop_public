import os
from dotenv import load_dotenv
from strtobool import stringtobool

load_dotenv()
HEADLESS = stringtobool(os.getenv("HEADLESS"))