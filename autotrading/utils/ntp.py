import ntplib
from time import ctime
import subprocess
import time

# NTP 서버 주소
NTP_SERVER = 'kr.pool.ntp.org'

# 최대 허용 시간 차이 (초)
MAX_TIME_DIFFERENCE = 0.5# 1분

def get_ntp_time():
    client = ntplib.NTPClient()
    response = client.request(NTP_SERVER, version=3)
    return response.tx_time

def get_local_time():
    return time.time()

def sync_time():
    try:
        subprocess.run(['sudo', 'ntpdate', NTP_SERVER], check=True)
        print(f"시간 동기화 성공: {ctime()}")

    except subprocess.CalledProcessError as e:
        print(f"시간 동기화 실패: {e}")

def ntp_sync():
    ntp_time = get_ntp_time()
    local_time = get_local_time()

    time_difference = abs(ntp_time - local_time)

    # print(f"NTP 서버 시간: {ctime(ntp_time)}")
    # print(f"로컬 시간: {ctime(local_time)}")
    # print(f"시간 차이: {time_difference}초")

    if time_difference > MAX_TIME_DIFFERENCE:
        print(f"시간 차이: {time_difference}초")
        print("시간 차이가 너무 큽니다. 동기화 중...")
        sync_time()
    else:
        # print("시간 차이가 허용 범위 내에 있습니다.")
        pass
