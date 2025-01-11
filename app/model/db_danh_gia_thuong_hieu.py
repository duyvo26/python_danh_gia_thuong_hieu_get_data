# Import thư viện mysql-connector để kết nối với MySQL
import mysql.connector
from mysql.connector import Error
from app.config import settings


# Hàm kết nối đến cơ sở dữ liệu MySQL
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host=settings.HOST,  # Địa chỉ máy chủ MySQL
            database=settings.DATABASE,  # Tên cơ sở dữ liệu
            user=settings.USER,  # Tên người dùng
            password=settings.PASSWORD,  # Mật khẩu
        )
        if connection.is_connected():
            print("Kết nối thành công đến MySQL!")
            return connection
    except Error as e:
        print("Lỗi khi kết nối đến MySQL:", e)
    return None


# Hàm lấy dữ liệu từ bảng request_thuong_hieu_list
def get_request_thuong_hieu_list():
    connection = connect_to_mysql()
    if connection:
        try:
            query = """
            SELECT request_thuong_hieu_list.*, 
                request_thuong_hieu.name_thuong_hieu,
                request_thuong_hieu_list.start_date_thuong_hieu,
                request_thuong_hieu_list.end_date_thuong_hieu
            FROM request_thuong_hieu_list
            JOIN request_thuong_hieu 
                ON request_thuong_hieu.id_rq = request_thuong_hieu_list.id_rq
            WHERE request_thuong_hieu_list.status = 0;
            """
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows

        except Error as e:
            print("Lỗi khi thực hiện truy vấn:", e)
        finally:
            cursor.close()
            connection.close()
            print("Kết nối MySQL đã được đóng.")


# Hàm cập nhật google_html và status của một bản ghi
def update_request_thuong_hieu_list(id_rq_list, google_html, status):
    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor()

            # Kiểm tra xem bản ghi có tồn tại không
            select_query = "SELECT * FROM request_thuong_hieu_list WHERE id_rq_list = %s"
            cursor.execute(select_query, (id_rq_list,))
            record = cursor.fetchone()

            if record:
                # Nếu bản ghi tồn tại, tiến hành cập nhật
                update_query = """
                    UPDATE request_thuong_hieu_list
                    SET google_html = %s, status = %s
                    WHERE id_rq_list = %s
                """
                cursor.execute(update_query, (google_html, status, id_rq_list))
                connection.commit()
                print(f"Cập nhật thành công bản ghi với id_rq_list = {id_rq_list}")
            else:
                print(f"Không tìm thấy bản ghi với id_rq_list = {id_rq_list}")

        except Error as e:
            print("Lỗi khi thực hiện truy vấn:", e)
        finally:
            cursor.close()
            connection.close()
            print("Kết nối MySQL đã được đóng.")
