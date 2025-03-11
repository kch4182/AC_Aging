'''ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡApp_Name 수정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'''
# 1. 설치할 App 
apps_to_install = ["Movies&TV","NETFLI", "USA today", "FOX Sports", "Accu weather", "Plex", "TED TV", "PBS KIDS Video", 
                   "Tune in", "VLC", "Kitchen Stories", "Amazon Video", "Haystack News", "Kodi", "The Weather Network", "Weathe", 
                   "Photo Gallery and Screensaver","AirAttack", "Dailymotion", "CNBC"]

'''ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡApp_Name 수정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'''

# import uiautomator2 as u2
import subprocess, sys, time, os

try :
    import uiautomator2 as u2
except :
    subprocess.check_call([sys.executable, "-m", "pip", "install", "uiautomator2"])
    print("프로그램을 재시작합니다")
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    os.execl(sys.executable, sys.executable, *sys.argv)  # 프로그램 재시작


print("구글 언어 English로 되있어야 정상 동작")
print("STB 연결 실패 or 정상 작동하지 않아 키보드가 뜨지 않는다면 구글 설정에서 Gboard Keyboard로 변경해야 함")
# 1.1. 연결 되어 있는 adb 제거
def kill_server() :
    try :
        subprocess.run(["adb", "kill-server"], check=True)
        print("adb kill-server 성공")
    except Exception as e :
        print('adb kill-server 실패', e)
        
kill_server()

# 2. STB 연결
def connect_STB() :
    try:
        ipv4 = input('STB IPV4 입력 : ')
        subprocess.run(["adb", "connect", ipv4], check=True) 
        # device 전역변수 설정
        global device
        device = u2.connect(ipv4)  # STB IP 주소
        print('STB 연결 완료')
        device.shell("ime set com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME")
        return device
    except Exception as e:
        print('STB 연결 실패', e)
        print('STB 개발자 모드 ON or IP 확인 필요')
        # 재귀함수로 STB 연결될 때까지 다시 실행
        connect_STB()
# 2.1 STB 연결 함수 실행
connect_STB()

# 2.2 연결 후 첫 진입
device.app_start("com.android.vending")  # Google Play 패키지 이름
time.sleep(1.5)

# Main APP 설치 함수
def install():      
    print("초기 접속 대기 2초")
    time.sleep(2)
    # 3. 앱 설치 자동화 함수 정의
    def install_app(app_name):
        # 3.1 Google Play 실행
        device.app_start("com.android.vending")  # Google Play 패키지 이름
        time.sleep(1.5)

        # 3.2 검색창 이동
        # 위로 이동
        device.shell("input keyevent 19")
        time.sleep(0.5)
        # 왼쪽으로 이동
        device.shell("input keyevent 21")
        time.sleep(0.5)
        # 아래쪽으로 이동
        device.shell("input keyevent 20")
        time.sleep(0.5)
        # 오른쪽으로 이동
        device.shell("input keyevent 22")
        time.sleep(0.5)

        # 3.2 검색어 입력
        device.send_keys(app_name)
        time.sleep(3.5)
        
        # 3.3설치 버튼 클릭
        install_button = device(text="Install")
        install_already_1 = device(text="Open")
        install_already_2 = device(text="Play")
        install_already_3 = device(text="Update")

        # 1) 검색 결과 Install 버튼이 있으면 설치 시작
        if install_button.exists :
            
            install_button.click()
            print(f"{app_name} 설치 시작")

            # 이용 가능 App 추가
            if app_name not in available :
                available.append(app_name)
        # 2) 검색 결과 Update 버튼이 있으면 업데이트 시작
        elif install_already_3.exists:
            install_already_3.click()
            print(f"{app_name} 업데이트 설치 시작")
            
            if app_name not in available :
                available.append(app_name)

        # 3) 이미 설치된 앱 넘어감
        elif install_already_1.exists or install_already_2.exists : 
            print(f"{app_name} 이미 설치된 앱")
            
            # 설치된 App 추가
            if app_name not in available :
                available.append(app_name)
        
        # 4) 검색 결과가 정확하지 않으면 첫 번째 있는 앱 설치
        else:
            # device(resourceId="com.android.vending:id/play_card").click()
            # 아래쪽으로 이동
            device.shell("input keyevent 20")
            time.sleep(1)
            xml_source = device.dump_hierarchy()
            # print(xml_source)
            
            # enter Click 하기 전에 한번 Search 하고 isn't가 없다면 이용불가 없다면 설치
            if "isn’t" in xml_source:
                print(f"{app_name} 해당 device 이용 불가.")
                # 이용 불가 App 추가
                if app_name not in not_available :
                    not_available.append(app_name)
                
            else :
                # 첫 번째 있는 App 선택
                device.press("enter")
                time.sleep(1)
                # Install or Update 있으면 설치
                if install_button.exists :
                    install_button.click()
                    print(f"{app_name} 설치 중 => 앱 Name 불일치 -> 확인 필요")
                    if app_name not in iffy_app :
                        iffy_app.append(app_name)
                elif install_already_3.exists: 
                    install_already_3.click()
                    print(f"{app_name} 업데이트 중 => 앱 Name 불일치 -> 확인 필요")
                    if app_name not in iffy_app :
                        iffy_app.append(app_name)
                # Open or Play 있으면 넘어감
                elif install_already_1.exists or install_already_2.exists : 
                    print(f"{app_name} 이미 설치된 앱")
                    if app_name not in iffy_app :
                        iffy_app.append(app_name)
                    
    # 설치된 앱 List
    available = []
    # 설치 확인 필요한 앱
    iffy_app = []
    # 해당 Device 사용 불가 List
    not_available = []

    # 4. 반복문 돌림
    for app in apps_to_install:
        install_app(app)
        time.sleep(1.5)  # 각 앱 설치 후 잠시 대기
        
        # adbkeyboard -> gboard로 변경
        device.shell("ime set com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME")

    print("1. 설치된 앱", available)
    print("")
    print("2. 확인 필요한 앱", iffy_app)
    print("")
    print("3. 해당 Device 불가 앱", not_available)

    while True :
        quit_input = input("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        if quit_input.lower() =="q":
            break
            

# 여기서 최종 실행
# 4.1 로그인이 안되어 있다면 자동 로그인
no_Sign = device(text="Sign in")
if no_Sign.exists :
    print("로그인 되어 있지 않아 공용 아이디로 로그인")
    device.press("enter")
    time.sleep(1)
    device.press("enter")
    time.sleep(6)
    device.send_keys("sqa01234@gmail.com")
    device.press("enter")
    time.sleep(5)
    device.send_keys("sqa0123456!")
    device.press("enter")
    print("로그인 성공 : Loading 중")
    time.sleep(6)
    install()

# 4.2 로그인 되어있다면 앱 설치 실행
else :
    install()


