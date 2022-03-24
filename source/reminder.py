import requests
import os
from dotenv import load_dotenv
load_dotenv()

MY_ENV_VAR = os.getenv('BITBUCKETAPPPASSWORD')
print(MY_ENV_VAR)

class BitBucket():
    def __init__(self) -> None:
        pass
