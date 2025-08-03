from app.service.get_data_google import GetDataGoogle
import time


if __name__ == "__main__":
    while True:
        try:
            GetDataGoogle().run()
        except Exception as _:
            pass
        finally:
            [time.sleep(1) or print("Null data:", _time) for _time in range(0, 10)]
