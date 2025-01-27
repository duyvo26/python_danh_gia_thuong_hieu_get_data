from app.service.process_data_from_google import ProcessDataFromGoogle
import time

if __name__ == "__main__":
    while True:
        try:
            ProcessDataFromGoogle().run()
        except Exception as _:
            pass
        finally:
            [time.sleep(1) or print("Null data:", _time) for _time in range(0, 10)]
