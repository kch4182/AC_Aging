# Android_STB Exo_Player 설치
import subprocess, sys, os, time
from datetime import datetime

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



# 2. 로그 추출 함수
def log_check():
    log_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
    
    # 바탕화면에 Log 폴더 생성
    log_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Log")
    os.makedirs(log_folder, exist_ok=True)  # 폴더가 없으면 생성
    
    # 로그 파일 경로 설정
    log_save_path = os.path.join(log_folder, log_filename)
    
    try:
        print("로그 추출 중...")
        with open(log_save_path, "w", encoding="utf-8") as log_file:
            subprocess.run(["adb", "logcat", "-d"], stdout=log_file, check=True)  # stdout을 파일로 리다이렉트
        print("로그 저장 완료")
        print("로그 저장 명 : ", log_save_path)
        device.shell("ime set com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME")
    except subprocess.CalledProcessError as e:
        print("로그 추출 실패:", e)
        device.shell("ime set com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME")


# 2.2 로그 추출 실행
log_check()
os.system('pause')












