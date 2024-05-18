# import subprocess

# def enable_ntp_sync():
#     try:
#         subprocess.run(['sudo', 'timedatectl', 'set-ntp', 'true'], check=True)
#         print("NTP 동기화가 활성화되었습니다.")
#     except subprocess.CalledProcessError as e:
#         print(f"명령 실행 중 오류가 발생했습니다: {e}")

# enable_ntp_sync()

import pexpect
print('시작')
def run_sudo_command(command, password):
    try:
        print(command, password)
        # 'sudo' 명령어를 실행하기 위한 pexpect 스크립트
        prompt = "password for {}: ".format(pexpect.run(command).decode().strip())
        child = pexpect.spawn(command, encoding='utf-8')

        # sudo가 암호를 요청하면 암호를 입력
        child.expect(prompt)
        child.sendline(password)

        # 명령어의 실행 결과를 출력
        child.expect(pexpect.EOF)
        print(child.before)
    except Exception as e:
        print('에러:',e)


# 사용 예제
sudo_password = "8318"  # 여기에 실제 sudo 암호를 입력하세요
run_sudo_command("sudo ls /root", sudo_password)
