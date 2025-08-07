import mysql.connector
from app.config import settings
import time
from app.model.db_danh_gia_thuong_hieu import insert_request_thuong_hieu_list


conn = mysql.connector.connect(
    host=settings.HOST,  # Địa chỉ máy chủ MySQL
    database=settings.DATABASE,  # Tên cơ sở dữ liệu
    user=settings.USER,  # Tên người dùng
    password=settings.PASSWORD,  # Mật khẩu
)
cursor = conn.cursor(dictionary=True)


query = "SELECT * FROM `request_thuong_hieu` WHERE `status` IN (0, 1) AND `data` IS NULL;"
cursor.execute(query)
result = cursor.fetchall()
for data in result:
    print("***************************")
    print("id_rq", data["id_rq"])

    query = f"SELECT * FROM `request_thuong_hieu_list` WHERE `id_rq` = {data['id_rq']}"
    cursor.execute(query)
    result = cursor.fetchall()
    print(len(result))

    if len(result) == 0:
        insert_request_thuong_hieu_list(id_rq=data["id_rq"], n_months=6, m_days=14)
    print("***************************")
