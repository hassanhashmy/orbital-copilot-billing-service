from decouple import config

ORBITAL_COPILOT_BASE_URL = config("ORBITAL_COPILOT_BASE_URL", default="https://owpublic.blob.core.windows.net/tech-task")
