import numpy as np
from PIL import ImageGrab
import time, csv, os, sys, cv2
from datetime import datetime

#******************STB Model 마다 변경해야 할 거******************
AC_AGING_IRIS = tuple(map(int,sys.argv[14].strip("()").split(", ")))   # 1. Booting 완료 색상(IRIS)
AC_AGING_SMART = tuple(map(int,sys.argv[16].strip("()").split(", ")))  # 2. Booting 완료 색상(SMART)
CAPTURE_INTERVAL = 0.3              # 5. 캡처 간격

MOVE_IRIS = tuple(map(int,sys.argv[18].strip("()").split(", ")))
MOVE_SMART = tuple(map(int,sys.argv[20].strip("()").split(", ")))
#******************STB Model 마다 변경해야 할 거******************

# *********************************IRIS or SmartViewer Tool 적용*********************************
BLUE_RGB_IRIS = (10,4,240)  # IRIS 화면 Blue (2, 231, 5)print("여기 확인 필요")
BLUE_RGB_SMART = (8, 8, 252)  # SmartViewer화면 Blue

# Tool 받아옴
select_tool_value = str(sys.argv[12])
print("선택 Program : ", select_tool_value)
if select_tool_value == "IRIS" :
    BLUE_RGB = BLUE_RGB_IRIS
    AC_AGING = AC_AGING_IRIS
    x_move = MOVE_IRIS[0] # 3. 각 화면에서 움직일 x축
    y_move = MOVE_IRIS[1] # 4. 각 화면에서 움직일 y축
else :
    BLUE_RGB = BLUE_RGB_SMART
    AC_AGING = AC_AGING_SMART
    x_move = MOVE_SMART[0] # 3. 각 화면에서 움직일 x축
    y_move = MOVE_SMART[1] # 4. 각 화면에서 움직일 y축
#*********************************IRIS or SmartViewer Tool 적용*********************************

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ변수 설정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
STB_POSITIONS = [
    (0, 0), (640, 0), (1280, 0),
    (0, 360), (640, 360), (1280, 360),
    (0, 720), (640, 720), (1280, 720)
]
STB_POSITIONS = [(x + x_move, y + y_move) for x, y in STB_POSITIONS] # SMARTVIEWER 16:9 => 9개 layout

STB_AC_LIST = sys.argv[2].split(',')  # list로 반환해야 함
STB_AC_LIST = [int(STB_AC_LIST[i])-1 for i in range(len(STB_AC_LIST))] # List index - 1 해서 실제 값
STB_AC_LIST_N = len(STB_AC_LIST) # List 개수
# AC_적용 STB 위치
STB_AC_POSITIONS = [STB_POSITIONS[i] for i in STB_AC_LIST]

# AC 설정 관련 변수
STB_AC_ON_TIME = int(sys.argv[4])
STB_AC_OFF_TIME = int(sys.argv[6])
STB_AC_CHECK_TIME = int(sys.argv[8])

# AC ON 기준 STB Input
STB_AC_CHECK = STB_AC_LIST[0]  # List[0]을 기준으로 AC Check 기준 잡음
STB_AC_CHECK_POSITIONS = [STB_POSITIONS[STB_AC_CHECK]]

print(f"STB_AC_LIST_N: {STB_AC_LIST_N}")
print(f"STB_AC_LIST: {STB_AC_LIST}")
print(f"STB_AC_POSITIONS: {STB_AC_POSITIONS}")
print(f"On Time: {STB_AC_ON_TIME}")
print(f"Off Time: {STB_AC_OFF_TIME}")
print(f"Check Time: {STB_AC_CHECK_TIME}")
print("STB_AC_CHECK_POSITIONS:", STB_AC_CHECK_POSITIONS)

# 색상 기준
BLACK_RGB = (12, 12, 12)  # 화면 Black

# 첫 부팅 시간 저장
start_time = None

# 로그 관련
START_DAY = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
stb_log_status = {f"STB {STB_AC_LIST[i]+1}": {"start_time": None} for i in range(len(STB_AC_LIST))}
log_path = sys.argv[10] # log 저장 경로
stb_rgb_counts = {
    f"STB {i+1}": {"screen_black": 0,"screen_blue":0,"screen_stop":0, "last_rgb": None, "black_count" :0, "last_rgb2": None} for i in range(len(STB_POSITIONS))
}
print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡTest STB Numberㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
j = 0
for i in STB_AC_LIST :
    print(f"{j+1}. STB {i+1}")
    j += 1
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ변수 설정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

# 1. 캡처 함수
def capture_screen():
    """1920x1080 화면을 캡처하고 RGB 배열 반환"""
    screenshot = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
    return np.array(screenshot.convert("RGB"))

# 2. 좌표 확인용 함수
def show_stb_positions(image, positions, scale=0.5):  # 화면 축소 비율
    # 화면 축소
    small_image = cv2.resize(image, (0, 0), fx=scale, fy=scale)  # fx, fy: 가로, 세로 비율 설정

    # OpenCV에서 사용할 이미지로 변환 (Pillow 이미지를 BGR 형식으로 변환)
    image_bgr = cv2.cvtColor(small_image, cv2.COLOR_RGB2BGR)

    # 축소된 이미지의 좌표 변환
    scaled_positions = [(int(x * scale), int(y * scale)) for x, y in positions]

    # STB 포지션에 빨간 점 그리기
    for x, y in scaled_positions:
        cv2.circle(image_bgr, (x, y), 3, (0, 0, 255), -1)  # 빨간색 원

    # 이미지 창 띄우기
    cv2.imshow("STB Positions (Small View)", image_bgr)

    # 7초 동안 창을 표시한 후 자동 닫기
    cv2.waitKey(7000)
    cv2.destroyAllWindows()  # 창 닫기

# 3. 로그 기록 함수
def log_event(stb_key, event, already_flag):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_time2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    compare_log = ["stb :", stb_key, "time : ", current_time, "event :", event ]
    if already_flag != compare_log :  # 이미 기록된 시간과 같으면 기록 안함
        print(f"[{current_time2}] : {stb_key} : {event} 로그 저장")
        # 경로가 존재하지 않으면 생성0
        os.makedirs(log_path, exist_ok=True)
        
        log_file = os.path.join(log_path, f"{START_DAY}.csv")
        
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ stb_key, current_time2,event])
        
        already_flag = compare_log  # 기록 후 flag 갱신
            
    return already_flag  # 갱신된 flag 반환

# 4. 정각 로그
def log_task():
    global last_hour_logged
    current_time = datetime.now()
    current_hour = current_time.hour
    if last_hour_logged != current_hour:
        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ정각 로그ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        last_hour_logged = current_hour

last_hour_logged = -10


#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡMain 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# 5. 각 STB에 대해 상태 확인 및 AC 연산
def ac_check(image, positions, off_check_time, STB_AC_LIST):
    global start_time
    for i, (x, y) in enumerate(positions):
        rgb = tuple(image[y, x])
        stb_key = f"STB {STB_AC_LIST[i]+1}"
        # 1. BLUE_RGB_IRIS 상태가 일정 시간 동안 유지되면 start_time 기록
        if np.linalg.norm(np.array(rgb) - np.array(BLUE_RGB)) < 15 :
            if start_time is None:
                start_time = datetime.now()  # BLUE_RGB_IRIS 상태가 지 속되면 start_time 기록
            current_time2_1 = datetime.now()
            
            # 화면이 BLUE_RGB_IRIS 상태가 유지된 시간이 off_check_time 이상이면 시간 Check
            if start_time is not None and int((datetime.now() - start_time).total_seconds()) >= off_check_time:
                print(f"{stb_key}: IRIS 상태가 {off_check_time}초 동안 유지됨")
                current_time2_2 = datetime.now()
                
                while True:
                    if int((datetime.now() - start_time).total_seconds())>= (STB_AC_CHECK_TIME + STB_AC_OFF_TIME):
                        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ연산 시작ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                        current_time2_3 = datetime.now()
                        timetime = current_time2_3 - start_time
                        for _ in range(20):
                            # 캡처 화면 update
                            image_check = capture_screen()
                            error_check(image_check, STB_AC_POSITIONS, stb_log_status)
                        start_time = None
                        break

        # BLUE_RGB_IRIS 상태가 지속되지 않는다면 start_time 초기화                
        elif start_time is not None:
            start_time = None  # IRIS 상태가 끊어지면 start_time 초기화

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡMain 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ    


#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡError Check 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# Error Check 함수
def error_check(image, positions, stb_log_status):
    global stb_rgb_counts
    for i, (x, y) in enumerate(positions):
        rgb = tuple(image[y, x])
        stb_key = f"STB {STB_AC_LIST[i]+1}"
        # 중복 IF문 진입 방지
        already_flag = stb_log_status[stb_key].get("last_log", None)
        # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        # 1. Black Screen 체크
        if np.linalg.norm(np.array(rgb) - np.array(BLACK_RGB)) < 15:
            stb_rgb_counts[stb_key]["black_count"] += 1 # black_count => 2번 찍히면 log 저장
            stb_rgb_counts[stb_key]["screen_black"] += 1 # count => 0.3초마다 한번 찍힘
            
            if stb_rgb_counts[stb_key]["black_count"] == 2 :
                stb_log_status[stb_key]["last_log"] = log_event(stb_key, "Black Screen 의심", already_flag)
                stb_rgb_counts[stb_key]["black_count"] = 0
    
            
            elif stb_rgb_counts[stb_key]["screen_black"] > 200 : # (CAPTURE_INTERVAL * 200)* 1 :  60초 * 4 => 4분 이상 지속되면 로그 찍지 않음
                # 첫 rgb 값이 None이면 rgb 값 업데이트
                if stb_rgb_counts[stb_key]["last_rgb"] is None : 
                    stb_rgb_counts[stb_key]["last_rgb"] = np.array(rgb)

              
                # None 값도 아니고 이전 last_rgb 값과 비슷하지 않다면 값 초기화 
                else :
                    # 업데이트 후 이전 last_rgb 값이 유지된다면 로그 찍지 않음
                    if np.linalg.norm(np.array(rgb) - np.array(stb_rgb_counts[stb_key]["last_rgb"])) < 15 :
                        pass
        
        # Black이 아니면 초기화       
        else :
            stb_rgb_counts[stb_key]["black_count"] = 0
            stb_rgb_counts[stb_key]["screen_black"] = 0
            stb_rgb_counts[stb_key]["last_rgb"] = None
            
             
        # 2. Screen 끊김 체크
        if np.linalg.norm(np.array(rgb) - np.array(BLUE_RGB)) < 15 :
            stb_rgb_counts[stb_key]["screen_blue"] += 1 # count => 10번 찍히면 
            
            if stb_rgb_counts[stb_key]["screen_blue"] > 200 : # (CAPTURE_INTERVAL * 200)* 1 :  60초 * 4 => 4분 이상 지속되면 로그 찍지 않음
                # 첫 rgb 값이 None이면 rgb 값 업데이트
                if stb_rgb_counts[stb_key]["last_rgb"] is None : 
                    stb_rgb_counts[stb_key]["last_rgb"] = np.array(rgb)
              
                # None 값도 아니고 이전 last_rgb 값과 비슷하지 않다면 값 초기화 
                else :
                    # 업데이트 후 이전 last_rgb 값이 유지된다면 로그 찍지 않음
                    if np.linalg.norm(np.array(rgb) - np.array(stb_rgb_counts[stb_key]["last_rgb"])) < 15 :
                        pass
            else : 
                stb_log_status[stb_key]["last_log"] = log_event(stb_key, "Screen 끊김 의심", already_flag)
        # Blue가 아니면 초기화
        else : 
            stb_rgb_counts[stb_key]["screen_blue"] = 0
            stb_rgb_counts[stb_key]["last_rgb"] = None

        
        # 3. Aging Complete 색상 체크 
        if np.linalg.norm(np.array(rgb) - np.array(AC_AGING)) <  20 :
            stb_rgb_counts[stb_key]["screen_stop"] = 0
            stb_rgb_counts[stb_key]["last_rgb2"] = None
            pass

        elif np.linalg.norm(np.array(rgb) - np.array(BLUE_RGB)) < 15 or np.linalg.norm(np.array(rgb) - np.array(BLACK_RGB)) < 15 :
            stb_rgb_counts[stb_key]["screen_stop"] = 0
            stb_rgb_counts[stb_key]["last_rgb2"] = None
            pass
        
        # 4. Aging Complete 색상과 비슷하지 않으면 Log 찍음
        else  :
            stb_rgb_counts[stb_key]["screen_stop"] += 1 # count => 10번 찍히면 
            if stb_rgb_counts[stb_key]["screen_stop"] > 200 : # (CAPTURE_INTERVAL * 200)* 1 :  60초 * 4 => 4분 이상 지속되면 로그 찍지 않음
                # 첫 rgb 값이 None이면 rgb 값 업데이트
                if stb_rgb_counts[stb_key]["last_rgb2"] is None : 
                    stb_rgb_counts[stb_key]["last_rgb2"] = np.array(rgb)
              
                # None 값도 아니고 이전 last_rgb 값과 비슷하지 않다면 값 초기화 
                else :
                    # 업데이트 후 이전 last_rgb 값이 유지된다면 로그 찍지 않음
                    if np.linalg.norm(np.array(rgb) - np.array(stb_rgb_counts[stb_key]["last_rgb2"])) < 20 :
                        pass
            else :
                stb_log_status[stb_key]["last_log"] = log_event(stb_key, "정상 부팅 X", already_flag)

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡError Check 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

def main():
    while True: 
        log_task()
        # Image 캡처
        image = capture_screen()
        # 각 STB 화면에 대해 check
        ac_check(image, STB_AC_CHECK_POSITIONS, STB_AC_OFF_TIME- 1, STB_AC_LIST)
        time.sleep(CAPTURE_INTERVAL)
        

print("강제종료 : Ctrl + C ")
print("***5초 후 Test 좌표 캡처 시작***IRIS or SMARTVIEWER 창 전체화면 후 최상단 배치***")
time.sleep(5)
screenshot = capture_screen()
show_stb_positions(screenshot, STB_AC_POSITIONS, scale=0.7)
print("5초 후 Youtube Aging Detecting Start ")
time.sleep(5)
print("Start Detecting")
main()    
 
