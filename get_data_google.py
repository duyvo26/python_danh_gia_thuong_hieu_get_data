from app.service.get_data_google import GetDataGoogle
import time
from app.model.db_danh_gia_thuong_hieu import insert_request_thuong_hieu_list
from app.model.db_danh_gia_thuong_hieu import get_request_thuong_hieu_chua_tao_list

if __name__ == "__main__":
    while True:
        danh_sach = get_request_thuong_hieu_chua_tao_list()
        for item in danh_sach:
            print(item["id_rq"])

            insert_request_thuong_hieu_list(id_rq=item["id_rq"], n_months=6, m_days=14)

        try:
            GetDataGoogle().run()
        except Exception as _:
            pass
        finally:
            [time.sleep(1) or print("Null data:", _time) for _time in range(0, 10)]
