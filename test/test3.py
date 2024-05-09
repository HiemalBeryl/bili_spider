import pymysql


def save_batch_into_db(data_list: list, table_name: str):
    if not data_list:
        print("数据为空，无需插入。")
        return

    try:
        connection = pymysql.connect(
            host=db_host, user=db_user, passwd=db_password, port=db_port, db=db_db
        )
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return

    cursor = connection.cursor()

    cols = ", ".join('`{}`'.format(k) for k in data_list[0].keys())

    val_cols = ', '.join('%({})s'.format(k) for k in data_list[0].keys())

    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({val_cols}) ON DUPLICATE KEY UPDATE "
    update_cols = ', '.join([f"{col}=VALUES({col})" for col in data_list[0].keys()])
    sql += update_cols

    try:
        # Prepare a list of dictionaries as required by executemany
        data = [tuple(item.values()) for item in data_list]

        cursor.executemany(sql, data)
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f'发生未知错误！{e}')
    finally:
        connection.close()


# 示例用法
data_list = [
    {"id": 1, "name": "John", "age": 30},
    {"id": 2, "name": "Alice", "age": 25},
    # Add more data dictionaries as needed
]

table_name = "your_table_name"

save_batch_into_db(data_list, table_name)