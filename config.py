import os

# Database credentials

USER = str(os.getenv("SNOWFLAKE_USER", ''))
PASSWORD = str(os.getenv("SNOWFLAKE_PASSWORD", ''))
ACCOUNT = str(os.getenv("SNOWFLAKE_ACCOUNT", ''))
WAREHOUSE = str(os.getenv("SNOWFLAKE_WAREHOUSE", ''))
DATABASE = str(os.getenv("SNOWFLAKE_DATABASE", ''))
SCHEMA = str(os.getenv("SNOWFLAKE_SCHEMA", ''))

# Environment variables for controlling whether this is a production deployment

TARGET = str(os.getenv("BLT_SMART_EVENTS_TARGET", 'DEV'))
EVENT_ID = str(os.getenv("BLT_SMART_EVENTS_EVENT_ID", ''))
PRICE_RANGE = float(os.getenv("BLT_SMART_EVENTS_PRICE_RANGE", "0.1"))
SIMILAR_EVENTS = str(os.getenv("BLT_SMART_EVENTS_SIMILAR_EVENTS", ''))

# Constants
ORANGE = '#FF8766'
BLUE = '#5E9FEC'
ORANGE_TRANS = '#FFDAD1'
GREY_LIGHT = '#353F48'
WHITE1 = '#FAFAFA'
GREY_DARK = '#545763'
LOGO = 'BoletiaLogoOrange.png'
