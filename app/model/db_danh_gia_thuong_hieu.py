# Import thư viện mysql-connector để kết nối với MySQL
import mysql.connector
from mysql.connector import Error
from app.config import settings
from datetime import datetime, timedelta


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
            # print("successful_connection_to_mysql!")
            return connection
    except Error as e:
        print("error_connecting_to_mysql:", e)
    return None


def get_request_thuong_hieu_chua_tao_list():
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)  # Trả kết quả dưới dạng dict

    query = """
        SELECT *
        FROM request_thuong_hieu
        WHERE status = 0
        AND id_rq NOT IN (
            SELECT DISTINCT id_rq FROM request_thuong_hieu_list
        )
    """

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def insert_request_thuong_hieu_list(id_rq: int, n_months: int, m_days: int):
    """
    Thêm dữ liệu vào bảng request_thuong_hieu_list cho id_rq.
    - Chia khoảng từ tháng hiện tại lùi về N tháng.
    - Mỗi dòng tương ứng với khoảng M ngày.
    - Bỏ qua nếu đã tồn tại (id_rq, start_date, end_date).
    """

    connection = connect_to_mysql()
    cursor = connection.cursor()

    today = datetime.today()
    # Ngày bắt đầu là ngày 1 của tháng (N tháng trước)
    start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    start_date = start_date - timedelta(days=(n_months - 1) * 30)  # lùi về ~N tháng

    end_date = today
    date_pairs = []

    current_start = start_date

    while current_start < end_date:
        current_end = current_start + timedelta(days=m_days - 1)
        if current_end > end_date:
            current_end = end_date
        date_pairs.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
        current_start = current_end + timedelta(days=1)

    # Lấy danh sách đã tồn tại
    select_query = """
        SELECT start_date_thuong_hieu, end_date_thuong_hieu
        FROM request_thuong_hieu_list
        WHERE id_rq = %s
    """
    cursor.execute(select_query, (id_rq,))
    existing = set(cursor.fetchall())

    # Chèn dữ liệu nếu chưa tồn tại
    insert_query = """
        INSERT INTO request_thuong_hieu_list (
            id_rq, start_date_thuong_hieu, end_date_thuong_hieu, status, google_html
        ) VALUES (%s, %s, %s, %s, %s)
    """

    inserted_count = 0
    for start, end in date_pairs:
        if (start, end) in existing:
            continue
        cursor.execute(insert_query, (id_rq, start, end, 0, None))
        inserted_count += 1

    connection.commit()
    cursor.close()
    connection.close()

    print(f"✅ Đã thêm {inserted_count} dòng mới cho id_rq = {id_rq}.")


def get_number_thuong_hieu(id_rq):
    connection = connect_to_mysql()
    if not connection:
        print("Không kết nối được MySQL")
        return 0

    try:
        cursor = connection.cursor()
        query = """
            SELECT COUNT(*) FROM `data_thuong_hieu`
            WHERE `id_rq` = %s
        """
        cursor.execute(query, (id_rq,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Error as e:
        print("Lỗi truy vấn:", e)
        return 0
    finally:
        cursor.close()
        connection.close()


def insert_data_thuong_hieu(id_rq, title, keyword, page_content, docs, search_timeline):
    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor()
            # Lấy thời gian hiện tại cho datetime_data, created_at, và updated_at
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Kiểm tra xem bản ghi đã tồn tại trong bảng chưa
            check_query = """
            SELECT COUNT(*) FROM `data_thuong_hieu`
            WHERE `id_rq` = %s AND `title` = %s AND `keyword` = %s AND `page_content` = %s AND `datetime_data` = %s
            """
            check_data = (id_rq, title, keyword, page_content, search_timeline)
            cursor.execute(check_query, check_data)
            result = cursor.fetchone()

            # Nếu đã có bản ghi tồn tại, bỏ qua việc thêm dữ liệu
            if result[0] > 0:
                print("Data already exists, skipping insert.")
                return

            # Câu lệnh SQL để thêm dữ liệu
            query = """
            INSERT INTO `data_thuong_hieu` (`id_rq`, `title`, `keyword`, `page_content`, `docs`, `datetime_data`, `created_at`, `updated_at`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Dữ liệu cần thêm
            data = (id_rq, title, keyword, page_content, docs, search_timeline, current_time, current_time)

            # Thực thi câu lệnh SQL
            cursor.execute(query, data)
            connection.commit()
            print("Data added successfully!")
        except Error as e:
            print("Error adding data:", e)
        finally:
            # Đóng kết nối và con trỏ
            cursor.close()
            connection.close()
    else:
        print("Unable to connect to MySQL to add data.")


# Hàm lấy dữ liệu từ bảng request_thuong_hieu_list


def load_get_request_thuong_hieu_list():
    # print("--load_get_request_thuong_hieu_list--")
    connection = connect_to_mysql()
    if connection:
        try:
            query = """
SELECT 
    rtl.*,
    rt.name_thuong_hieu,
    rt.email,
    rt.fullname
FROM 
    request_thuong_hieu_list rtl
JOIN 
    request_thuong_hieu rt 
    ON rt.id_rq = rtl.id_rq
JOIN 
    (
        SELECT 
            MAX(rtl_sub.id_rq_list) AS max_id
        FROM 
            request_thuong_hieu_list rtl_sub
        JOIN 
            request_thuong_hieu rt_sub 
            ON rt_sub.id_rq = rtl_sub.id_rq
        WHERE 
            (rtl_sub.status = 0 OR rtl_sub.google_html = '')
        GROUP BY 
            rt_sub.email, 
            rtl_sub.start_date_thuong_hieu, 
            rtl_sub.end_date_thuong_hieu
    ) latest 
    ON latest.max_id = rtl.id_rq_list
WHERE 
    rt.status IN (0, 1)
                """
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Error as e:
            print("get_request_thuong_hieu_list: unable_to_connect_to_mysql_to_add_data.", e)
        finally:
            cursor.close()
            connection.close()
            print("mysql_connection_has_been_closed.")


def get_request_thuong_hieu_list():
    return load_get_request_thuong_hieu_list()


def check_id_thuong_hieu_run():
    connection = connect_to_mysql()
    if connection:
        try:
            query = """
                SELECT  id_rq
                FROM request_thuong_hieu_list
                WHERE status = 1 AND google_html != '' 
                GROUP By id_rq
            """
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            _list_id_run = []

            for i in rows:
                _id_rq = i[0]
                print("i", _id_rq)
                query = f"""
                SELECT COUNT(id_rq) FROM `request_thuong_hieu_list` WHERE google_html = '' AND id_rq = {_id_rq}
                """
                cursor = connection.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                count_html_google = rows[0][0]
                print("count html google", count_html_google)
                if int(count_html_google) == 0:
                    _list_id_run.append(_id_rq)

            return _list_id_run

        except Error as e:
            print("error_while_executing_query:", e)
        finally:
            cursor.close()
            connection.close()
            print("check_id_thuong_hieu_run: mysql_connection_has_been_closed.")


def get_request_thuong_hieu_list_end(id_rq):
    connection = connect_to_mysql()
    if connection:
        try:
            query = f"""
            SELECT id_rq_list, 
                id_rq,
                google_html,
                start_date_thuong_hieu,
                end_date_thuong_hieu
                
            FROM request_thuong_hieu_list
            
            WHERE status = 1 AND google_html != '' AND id_rq = {id_rq};
            """
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows

        except Error as e:
            print("error_while_executing_query:", e)
        finally:
            cursor.close()
            connection.close()
            print("get_request_thuong_hieu_list_end: mysql_connection_has_been_closed.")


def get_brand_name(id_rq):
    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor()

            # Kiểm tra xem bản ghi có tồn tại không
            select_query = "SELECT * FROM request_thuong_hieu WHERE id_rq = %s"
            cursor.execute(select_query, (id_rq,))
            rows = cursor.fetchall()
            return rows

        except Error as e:
            print("error_while_executing_query:", e)
        finally:
            cursor.close()
            connection.close()
            print("get_brand_name: mysql_connection_has_been_closed.")


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
                print(f"successfully_updated_record_with_id_rq_list_= {id_rq_list}")
            else:
                print(f"no_record_found_with_id_rq_list= {id_rq_list}")

        except Error as e:
            print("update_request_thuong_hieu_list: error_while_executing_query:", e)
        finally:
            cursor.close()
            connection.close()
            print("mysql_connection_has_been_closed.")


def update_request_thuong_hieu_list_end(id_rq_list, status):
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
                    SET status = %s
                    WHERE id_rq_list = %s
                """
                cursor.execute(update_query, (status, id_rq_list))
                connection.commit()
                print(f"record_updated_successfully_with id_rq_list = {id_rq_list}")
            else:
                print(f"no_record_found_with_id_rq_list = {id_rq_list}")

        except Error as e:
            print("update_request_thuong_hieu_list_end: error_while_executing_query:", e)
        finally:
            cursor.close()
            connection.close()
            print("mysql_connection_has_been_closed.")
