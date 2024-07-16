import os

from dotenv import load_dotenv

current_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv(dotenv_path=f"{current_path}/.env.test", verbose=True, override=True)
