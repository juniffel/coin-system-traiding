import threading
import time
import autotrade
import bot

def worker_1():
    print("바이비트 API 작업을 실행합니다.")
    while 1:
        time.sleep(10)  # 2초 동안 작업 수행
        print("Worker 1 finished")

def worker_2():
    print("텔레그램 봇을 가동합니다.")
    while 1:
        time.sleep(1)  # 3초 동안 작업 수행
        print("Worker 2 finished")

if __name__ == '__main__':
    # 스레드 생성
    t1 = threading.Thread(target=worker_1)
    t2 = threading.Thread(target=worker_2)

    # 스레드 시작
    t1.start()
    t2.start()

    # 스레드 종료 대기
    t1.join()
    t2.join()

    print("All workers finished")
