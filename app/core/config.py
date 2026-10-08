import os
from typing import cast

from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL = cast(str, os.getenv("DATABASE_URL"))

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")