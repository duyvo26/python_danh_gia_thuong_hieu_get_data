from app.service.get_data_google import GetDataGoogle
import time
from app.model.db_danh_gia_thuong_hieu import insert_request_thuong_hieu_list
from app.model.db_danh_gia_thuong_hieu import connect_to_mysql


def add_data_sreach_google():
    connection = connect_to_mysql()

    cursor = connection.cursor()

    query = "SELECT * FROM `request_thuong_hieu` WHERE `status` IN (0, 1) AND `data` IS NULL;"
    cursor.execute(query)
    result = cursor.fetchall()
    for data in result:
        # print("***************************")
        # print(data)
        # print("id_rq", data[0])

        query = f"SELECT * FROM `request_thuong_hieu_list` WHERE `id_rq` = {data[0]}"
        cursor.execute(query)
        result = cursor.fetchall()
        # print(len(result))

        if len(result) == 0:
            insert_request_thuong_hieu_list(id_rq=data[0], n_months=6, m_days=14)
        # print("***************************")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    while True:
        try:
            add_data_sreach_google()

            GetDataGoogle().run()
        except Exception as e:
            print(e)
            pass
        finally:
            [time.sleep(1) or print("Null data:", _time) for _time in range(0, 5)]
