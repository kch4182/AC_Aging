import time, csv, sys, os, cv2
import numpy as np
from PIL import ImageGrab
from datetime import datetime

'''*********************************STB Model 마다 변경해야 할 거*********************************'''
BLUE_RGB_IRIS = tuple(map(int,sys.argv[8].strip("()").split(", ")))  # IRIS 화면 Blue
BLUE_RGB_SMART = tuple(map(int,sys.argv[10].strip("()").split(", ")))  # SmartViewer화면 Blue
YOUTUBE_24H_IRIS = tuple(map(int,sys.argv[12].strip("()").split(", ")))    # 1. Youtube 색상(IRIS)
YOUTUBE_24H_SMART = tuple(map(int,sys.argv[14].strip("()").split(", ")))   # 2. Youtube 색상(SMART)
# COMPLETE_IRIS = (134, 183, 205)   # 1. IRIS 연결 시 구분 RGB
# COMPLETE_SMART = (166, 217, 242)  # 2. SMARTVIEWER 연결 시 구분 RGB
x_move = 300                        # 3. 각 화면에서 움직일 x축
y_move = 100                        # 4. 각 화면에서 움직일 y축
CAPTURE_INTERVAL = 0.3              # 5. 캡처시간
AGING = "YOUTUBE"                   # 6. Aging 종류

'''*********************************STB Model 마다 변경해야 할 거*********************************'''

'''*********************************IRIS or SmartViewer Tool 적용*********************************'''
select_tool_value = str(sys.argv[6])
print("선택 Program : ", select_tool_value)
if select_tool_value == "IRIS" :
    BLUE_RGB = BLUE_RGB_IRIS
    YOUTUBE_24H = YOUTUBE_24H_IRIS
    # x_move
    # y_move
else : 
    BLUE_RGB = BLUE_RGB_SMART
    YOUTUBE_24H = YOUTUBE_24H_SMART
    # x_move
    # y_move
'''*********************************IRIS or SmartViewer Tool 적용*********************************'''

# DVR 화면 STB 좌표 : 기본 9개
STB_POSITIONS = [
    (0, 0), (640, 0), (1280, 0),
    (0, 360), (640, 360), (1280, 360),
    (0, 720), (640, 720), (1280, 720)
]

STB_POSITIONS = [(x + x_move, y + y_move) for x, y in STB_POSITIONS] # SMARTVIEWER 16:9 => 9개 layout

STB_AGING_LIST = sys.argv[2].split(',')
STB_AGING_LIST = [int(STB_AGING_LIST[i])-1 for i in range(len(STB_AGING_LIST))]
STB_AGING_POSITIONS = [STB_POSITIONS[i] for i in STB_AGING_LIST]

# 색상 기준
BLACK_RGB = (12, 12, 12)  # 화면 Black

# 첫 부팅 시간 저장
start_time = None

# 로그 관련
START_DAY = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
stb_log_status = {f"STB {STB_AGING_LIST[i]+1}": {"start_time": None} for i in range(len(STB_AGING_LIST))}
# 로그 저장 경로
log_path = sys.argv[4]

print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡTest STB Numberㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
j = 0
for i in STB_AGING_LIST :
    print(f"{j+1}. STB {i+1}")
    j += 1


# 캡처 함수
def capture_screen():
    screenshot = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
    return np.array(screenshot)

# 좌표 확인용 함수
def show_stb_positions(image, positions, scale=0.5):  # 화면 축소 비율
    # 화면 축소
    small_image = cv2.resize(image, (0, 0), fx=scale, fy=scale)  # fx, fy: 가로, 세로 비율 설정

    # OpenCV에서 사용할 이미A지로 변환 (Pillow 이미지를 BGR 형식으로 변환)
    image_bgr = cv2.cvtColor(small_image, cv2.COLOR_RGB2BGR)

    # 축소된 이미지의 좌표 변환
    scaled_positions = [(int(x * scale), int(y * scale)) for x, y in positions]

    # STB 포지션에 빨간 점 그리기
    for x, y in scaled_positions:
        cv2.circle(image_bgr, (x, y), 5, (0, 0, 255), -1)  # 빨간색 원

    # 이미지 창 띄우기
    cv2.imshow("STB Positions (Small View)", image_bgr)

    # 7초 동안 창을 표시한 후 자동 닫기
    cv2.waitKey(7000)
    cv2.destroyAllWindows()  # 창 닫기



# 로그 기록 함수
def log_event(stb_key, event, already_flag):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    compare_log = ["stb :", stb_key, "time : ", current_time, "event :", event ]
    if already_flag != compare_log :  # 이미 기록된 시간과 같으면 기록 안함
        print(f"{stb_key} : {event} 로그 저장")
        # 경로가 존재하지 않으면 생성
        os.makedirs(log_path, exist_ok=True)
        
        log_file = os.path.join(log_path, f"error_log_{START_DAY}.csv")
        
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([stb_key, current_time, event])
        
        already_flag = compare_log  # 기록 후 flag 갱신
            
    return already_flag  # 갱신된 flag 반환

# 정각 로그
def log_task():
    global last_hour_logged
    current_time = datetime.now()
    current_hour = current_time.hour
    if last_hour_logged != current_hour:
        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ정각 로그ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        last_hour_logged = current_hour

last_hour_logged = -1

### 상태 구분

stb_rgb_counts = {
    f"STB {i+1}": {"screen_black": 0,"screen_blue":0,"screen_stop":0, "last_rgb": None, "black_count" :0, "last_rgb2": None} for i in range(len(STB_POSITIONS))
}

'''ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡMain 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'''
# Error Check 함수
def error_check(image, positions, stb_log_status):
    global stb_rgb_counts
    for i, (x, y) in enumerate(positions):
        rgb = tuple(image[y, x])
        stb_key = f"STB {STB_AGING_LIST[i]+1}"
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

        
        # 3. Youtube 색상 체크 
        if np.linalg.norm(np.array(rgb) - np.array(YOUTUBE_24H)) <  20 :
            stb_rgb_counts[stb_key]["screen_stop"] = 0
            stb_rgb_counts[stb_key]["last_rgb2"] = None
            pass

        elif np.linalg.norm(np.array(rgb) - np.array(BLUE_RGB)) < 15 or np.linalg.norm(np.array(rgb) - np.array(BLACK_RGB)) < 15 :
            stb_rgb_counts[stb_key]["screen_stop"] = 0
            stb_rgb_counts[stb_key]["last_rgb2"] = None
            pass
        
        # 4. 24h 영상(Pink 색상) -> 기준으로 비슷하지 않다면 Log 저장
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
                stb_log_status[stb_key]["last_log"] = log_event(stb_key, "광고 확인 필요", already_flag)
        
'''ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡMain 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'''

# 메인 실행
def main():
    while True:
        log_task()
        image = capture_screen()
        error_check(image, STB_AGING_POSITIONS, stb_log_status)

        time.sleep(CAPTURE_INTERVAL)

print("강제종료 : Ctrl + C ")
print("***5초 후 Test 좌표 캡처 시작***IRIS or SMARTVIEWER 창 전체화면 후 최상단 배치***")
time.sleep(5)
screenshot = capture_screen()
show_stb_positions(screenshot, STB_AGING_POSITIONS, scale=0.7)
print("5초 후 Youtube Aging Detecting Start ")
time.sleep(5)
main()
