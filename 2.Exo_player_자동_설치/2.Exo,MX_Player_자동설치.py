# Android_STB Exo_Player 설치
import subprocess, sys, os, time

'''ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡExo_Player 경로 수정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'''
# 1) app 경로 수정
apps_to_install_Exo = os.path.join(os.path.dirname(__file__), "./ExoPlayer_play.apk")
apps_to_install_MX = os.path.join(os.path.dirname(__file__), "./MX_Player.apk")

'''ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡExo_Player 경로 수정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'''

try :
    import uiautomator2 as u2
except :
    subprocess.check_call([sys.executable, "-m", "pip", "install", "uiautomator2"])
    print("프로그램을 재시작합니다")
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    os.execl(sys.executable, sys.executable, *sys.argv)  # 프로그램 재시작
print("STB 연결 실패 or 정상 작동하지 않아 키보드가 뜨지 않는다면 구글 설정에서 Gboard Keyboard로 변경해야 함")

# 0. 연결 되어 있는 adb 제거
def kill_server() :
    try :
        subprocess.run(["adb", "kill-server"], check=True)
        print("adb kill-server 성공")
    except Exception as e :
        print('adb kill-server 실패', e)
        
kill_server()

# 1. STB 연결
def connect_STB() :
    try:
        ipv4 = input('STB IPV4 입력 : ')
        subprocess.run(["adb", "connect", ipv4], check=True) 
        # device 전역변수 설정
        global device
        device = u2.connect(ipv4)  # STB IP 주소
        print('STB 연결 완료')
        # STB Keyboard 변경
        device.shell("ime set com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME")
        return device
    except Exception as e:
        print('STB 연결 실패', e)
        print('STB 개발자 모드 ON or IP 확인 필요')
        # 재귀함수로 STB 연결될 때까지 다시 실행
        connect_STB()
# 1.1 STB 연결 함수 실행
connect_STB()

# 2. Exo_Player 설치
def install_Exo():
    try:
        print("Exo_Player 설치 중...")
        subprocess.run(["adb", "install", "-t", apps_to_install_Exo], check=True)
        print("Exo_Player 설치 완료")
    except subprocess.CalledProcessError as e:
        print("Exo_Player 설치 실패:", e)


# 2.2 설치 함수 실행
install_Exo()

time.sleep(2)

# 3. MX_Player 설치
def install_MX():
    try:
        print("MX_Player 설치 중...")
        subprocess.run(["adb", "install", "-t", apps_to_install_MX], check=True)
        print("MX_Player 설치 완료")
    except subprocess.CalledProcessError as e:
        print("MX_Player 설치 실패:", e)


# 3.2 설치 함수 실행
install_MX()

os.system('pause')












