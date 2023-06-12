def get_db_table_name(app_name: str, table_name: str, is_plural: bool = True) -> str:
    return f"{app_name}_{table_name}{'s' if is_plural else ''}"
