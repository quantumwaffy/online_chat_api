from core import utils as core_utils

from . import APP_NAME

user_table_name: str = core_utils.get_db_table_name(APP_NAME, "user")
role_table_name: str = core_utils.get_db_table_name(APP_NAME, "role")
