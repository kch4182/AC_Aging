import numpy as np
from PIL import ImageGrab
import time, csv, os, sys, cv2, ast, mss
from datetime import datetime

#******************STB Model 마다 변경해야 할 거******************
AC_AGING_IDIS = tuple(map(int,sys.argv[14].strip("()").split(", ")))   # 1. Booting 완료 색상(IDIS)
AC_AGING_SMART = tuple(map(int,sys.argv[16].strip("()").split(", ")))  # 2. Booting 완료 색상(SMART)
CAPTURE_INTERVAL = 0.3              # 5. 캡처 간격

MOVE_IDIS = tuple(map(int,sys.argv[18].strip("()").split(", ")))
MOVE_SMART = tuple(map(int,sys.argv[20].strip("()").split(", ")))
STB_NAME = str(sys.argv[22])
#******************STB Model 마다 변경해야 할 거******************

# *********************************IDIS or SmartViewer Tool 적용*********************************
BLUE_RGB_IDIS = (8,6,247)  # IDIS 화면 (450, 200) 좌표의 RGB 평균값

########################################################
# BLUE_RGB_SMART = (8, 8, 252)  # SmartViewer화면 Blue
BLUE_RGB_SMART = (31,31,31) # Composite 화면 끊김 변수
########################################################

STB_POSITIONS_IDIS  = [
    (0, 0), (640, 0), (1280, 0),
    (0, 360), (640, 360), (1280, 360),
    (0, 720), (640, 720), (1280, 720)
]
STB_POSITIONS_SMART = [
    (0, 0), (636, 0), (1272, 0),
    (0, 360), (636, 360), (1272, 360),
    (0, 720), (636, 720), (1272, 720)
]
# Tool 받아옴
select_tool_value = str(sys.argv[12])
if select_tool_value == "IDIS" :
    BLUE_RGB = BLUE_RGB_IDIS
    AC_AGING = AC_AGING_IDIS
    x_move = MOVE_IDIS[0] # 3. 각 화면에서 움직일 x축
    y_move = MOVE_IDIS[1] # 4. 각 화면에서 움직일 y축
    STB_POSITIONS_default = STB_POSITIONS_IDIS
else :
    BLUE_RGB = BLUE_RGB_SMART
    AC_AGING = AC_AGING_SMART
    x_move = MOVE_SMART[0] # 3. 각 화면에서 움직일 x축
    y_move = MOVE_SMART[1] # 4. 각 화면에서 움직일 y축
    STB_POSITIONS_default = STB_POSITIONS_SMART # SMARTVIEWER 맨 오른쪽에 Padding 10정도 있어 위치 수정
#*********************************IDIS or SmartViewer Tool 적용*********************************

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ변수 설정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

# 여기서 구분으로 GUI에서 STB 위치 받아옴
STB_POSITIONS = tuple(ast.literal_eval(sys.argv[24]))

# STB1 기준일 때 
if len(STB_POSITIONS) == 1 :
   STB_POSITIONS = [(x + STB_POSITIONS[0][0], y + STB_POSITIONS[0][1]) for x, y in STB_POSITIONS_default] # SMARTVIEWER 16:9 => 9개 layout    
# 개별마다 따로 설정할 때 그대로
else :
    # 각각의 좌표로 받는다면 Default 값으로 사용
    STB_POSITIONS_default = STB_POSITIONS_IDIS
    
###################################################

###################################################
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
# AC_CHECK 좌표를 고정시킬 거임
STB_POSITIONS_default = [(x+450, y+ 200) for x,y in STB_POSITIONS_default]
STB_AC_CHECK_POSITIONS = [STB_POSITIONS_default[STB_AC_CHECK]]

print(f"STB_AC_POSITIONS: {STB_AC_POSITIONS}")
print(f"Off Time: {STB_AC_OFF_TIME}")
print(f"Check Time: {STB_AC_CHECK_TIME}")

# 색상 기준
BLACK_RGB = (12, 12, 12)  # 화면 Black

# 첫 부팅 시간 저장
start_time = None

# 로그 관련
START_DAY = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
stb_log_status = {f"STB {STB_AC_LIST[i]+1}": {"start_time": None} for i in range(len(STB_AC_LIST))}
log_path = sys.argv[10] # log 저장 경로
stb_rgb_counts = {
    f"STB {i+1}": {"screen_black": 0,"screen_blue":0,"screen_stop":0, "last_rgb": None, "black_count" :0, "last_rgb2": None, "last_print":None,} for i in range(len(STB_POSITIONS))
}
stb_check_counts = {
    f"CHECK_STB {i+1}" : {"screen_blue":0} for j, i in enumerate(STB_AC_LIST)
}

print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡTest STB Numberㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
[print(f"{j+1}. STB {i+1}") for j, i in enumerate(STB_AC_LIST)]
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ변수 설정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# STB_AC_POSITIONS = [(-1685, 258), (-1044, 267), (-422, 269)]
# STB_AC_POSITIONS = [(-1600, 200), (-960, 200), (-320, 200)]

# 사용자의 모니터 해상도 
MAIN_WIDTH, MAIN_HEIGHT = 1920, 1080
SUB_WIDTH, SUB_HEIGHT = 1920, 1080
# ImageGrab : bbox = (x1, y1, x2, y2)
# mss : bbox = {"left": x1, "top": y1, "width": w, "height": h}
# 이런 식으로 인자값을 받아와서 left, top 좌표를 지정하고 여기서 해상도에 맞게 캡처
# ImageGrab은 Main화면에서 왼쪽 위 좌표부터 -> 오른쪽 아래 좌표까지 캡처
def capture_screen():
    """현재 모니터 위치에 따라 화면을 캡처하고 RGB 배열 반환"""
    x_pos = STB_AC_POSITIONS[0][0]  # STB 위치 정보

    with mss.mss() as sct:
        # 서브 모니터가 왼쪽에 있는 경우
        if x_pos < 0:
            # 좌측 서브 모니터 캡처: 화면이 음수 좌표에 있으므로 이를 처리
            bbox = {"left": -MAIN_WIDTH, "top": 0, "width": SUB_WIDTH, "height": MAIN_HEIGHT}
        # 서브 모니터가 오른쪽에 있는 경우
        elif x_pos > MAIN_WIDTH:
            bbox = {"left": MAIN_WIDTH, "top": 0, "width": SUB_WIDTH, "height": MAIN_HEIGHT}
        # 메인 모니터 캡처
        else:
            bbox = {"left": 0, "top": 0, "width": MAIN_WIDTH, "height": MAIN_HEIGHT}

        # 화면 캡처
        screenshot = sct.grab(bbox)
        # 캡처된 이미지를 RGB로 변환
        img = np.array(screenshot)  # BGRA -> BGR
        img = img[..., :3]  # Alpha 채널 제외하고 RGB만 추출
        screenshot = img[..., ::-1]  # BGR을 RGB로 변환
        return np.array(screenshot)
    
# 2. 좌표 확인용 함수
def show_stb_positions(image, positions, scale=0.6):  # 화면 축소 비율
    # 화면 축소
    small_image = cv2.resize(image, (0, 0), fx=scale, fy=scale)  # fx, fy: 가로, 세로 비율 설정

    # OpenCV에서 사용할 이미지로 변환 (Pillow 이미지를 BGR 형식으로 변환)
    image_bgr = cv2.cvtColor(small_image, cv2.COLOR_RGB2BGR)

    # 축소된 이미지의 좌표 변환
    scaled_positions = [(int(x * scale), int(y * scale)) for x, y in positions]
    # STB 포지션에 빨간 점 그리기
    for x, y in scaled_positions:
        # 좌표가 이미지 크기 내에 있는지 확인
        if 0 <= x < image_bgr.shape[1] and 0 <= y < image_bgr.shape[0]:
            cv2.circle(image_bgr, (x, y), 3, (0, 0, 255), -1)  # 빨간색 원
        else :
            pass

    # 이미지 창 띄우기
    cv2.imshow("STB Positions", image_bgr)

    # 7초 동안 창을 표시한 후 자동 닫기
    cv2.waitKey(7000)
    cv2.destroyAllWindows()  # 창 닫기
    
    # 사용한 이미지 메모리 해제
    small_image = None  
    image_bgr = None    
    del small_image     
    del image_bgr       

# 3. 로그 기록 함수
def log_event(stb_key, event, already_flag):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_time2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    compare_log = ["stb :", stb_key, "time : ", current_time, "event :", event ]
    if already_flag != compare_log :  # 이미 기록된 시간과 같으면 기록 안함
        print(f"[{current_time2}] : {stb_key} : {event} 로그 저장")
        # 경로가 존재하지 않으면 생성
        os.makedirs(log_path, exist_ok=True)
        
        log_file = os.path.join(log_path, f"{STB_NAME}_{START_DAY}.csv")
        
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ stb_key, current_time2,event])
        
        already_flag = compare_log  # 기록 후 flag 갱신
            
    return already_flag  # 갱신된 flag 반환

CHANGE_CHECK_STB = 0
#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡMain 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
def ac_check(image, positions, off_check_time, STB_AC_LIST):
    global start_time, stb_rgb_counts, STB_AC_CHECK, STB_AC_CHECK_POSITIONS, CHANGE_CHECK_STB, stb_check_counts
    for i, (x, y) in enumerate(positions):
         # 만약 서브 모니터에 해당하는 좌표라면
        if x >= MAIN_WIDTH:
            x = x - MAIN_WIDTH  # 서브 모니터 좌표를 메인 모니터에 맞게 변환

        rgb = tuple(image[y, x])
        # BLUE_RGB Check하는 stb_key
        stb_key = f"CHECK_STB {STB_AC_LIST[CHANGE_CHECK_STB]+1}"
        
        # 연산할 때 사용하는 stb_key
        error_check_stb = f"STB {STB_AC_LIST[CHANGE_CHECK_STB]+1}"

        # BLUE_RGB 상태 확인
        if np.linalg.norm(np.array(rgb) - np.array(BLUE_RGB)) < 20 :
            if start_time is None:
                start_time = datetime.now()  # 처음 상태 지속 시작 시간 기록
            ##################################################################
            # 여기다가 다음 Check 넘어가는 거 만들거임 -> 이거도 쉽진 않을듯
            stb_check_counts[stb_key]["screen_blue"] += 1 # 0.3초마다 하나씩 counts 1분이면 -> 200    
            
            # OFF과 Check 연산시 BLUE 계속 유지되면 Check STB 기준 넘어감
            if stb_check_counts[stb_key]["screen_blue"] > 70 : # 70
                already_flag= 0
                print(f"{stb_key} 이슈 발생 : 로그 저장(Check STB)")
                log_event(stb_key,"Check STB 기준 변경됨(확인필요)", 0)
                if int(STB_AC_LIST[CHANGE_CHECK_STB]) == int(STB_AC_LIST[-1]) :
                    print("모든 STB 사망... 프로그램 종료...")
                    os.system("pause")
                
                # 여기서 기준이 바뀜 -> 근데 1,3,4 이런 경우의 수도 생각해야 함
                # CHANGE_CHECK_STB +=1 이런 식으로 하면 오류 당연히 날듯
                CHANGE_CHECK_STB += 1
                STB_AC_CHECK = STB_AC_LIST[CHANGE_CHECK_STB]  #
                
                STB_AC_CHECK_POSITIONS = [STB_POSITIONS_default[STB_AC_CHECK]]
                
                stb_check_counts[stb_key]["screen_blue"] = 0 # 초기화
                break
            
            ##################################################################
            if start_time is not None and int((datetime.now() - start_time).total_seconds()) >= off_check_time:
                print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                print(f"[{datetime.now()}]{stb_key}: STB OFF가 {off_check_time}초 동안 유지됨", flush=True)
                # Program 시작 시간 저장
                DEAD_STB_COVER = datetime.now()
                time.sleep(0.5)
                while True:
                    first_print = True
                    # 연산 시작 조건 확인
                    if int((datetime.now() - start_time).total_seconds())>= (STB_AC_CHECK_TIME + STB_AC_OFF_TIME -0.5):
                        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ연산 시작ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ", flush=True)
                        for _ in range(10):
                            image_check = capture_screen()  # 캡처 화면 업데이트
                            stb_rgb_counts[error_check_stb]["last_print"] = error_check(image_check, STB_AC_POSITIONS, stb_log_status, first_print, rgb, stb_key)
                            first_print = False
                        start_time = None  # 연산 완료 후 초기화
                        # ON Time 충족할 때까지 while 문 계속 돌림
                        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ", flush=True)
                        while True :
                            if int((datetime.now() - DEAD_STB_COVER).total_seconds()) >= STB_AC_ON_TIME :
                                print(f"[{datetime.now()}] ON TIME 충족 : 프로그램 종료")
                                break

                        # print("total_seconds())",int((datetime.now() - DEAD_STB_COVER).total_seconds()))
                        break
                        
            image = None # 이미지가 사용하는 메모리 반납

        # BLUE_RGB_IDIS 상태가 지속되지 않는다면 start_time 초기화                
        elif start_time is not None:
            start_time = None  # IDIS 상태가 끊어지면 start_time 초기화

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡMain 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ    

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡError Check 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
# Error Check 함수
def error_check(image, positions, stb_log_status, first_print, check_rgb, check_stb_key):
    global stb_rgb_counts, stb_check_counts
    for i, (x, y) in enumerate(positions):
        if x >= MAIN_WIDTH:
            x = x - MAIN_WIDTH  # 서브 모니터 좌표를 메인 모니터에 맞게 변환
        rgb = tuple(image[y, x])
        stb_key = f"STB {STB_AC_LIST[i]+1}"
        # 중복 IF문 진입 방지
        already_flag = stb_log_status[stb_key].get("last_log", None)
        
        # 0. Check Positions BLUE_RGB CHECK
        if np.linalg.norm(np.array(check_rgb) - np.array(BLUE_RGB)) < 15: # Check_RGB가 Blue 이면 
            stb_check_counts[check_stb_key]["screen_blue"] += 1 # count => 10번 찍히면 

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

        #####################################################################
        # 3. Aging Complete 색상 체크 
        if np.linalg.norm(np.array(rgb) - np.array(AC_AGING)) <  35 :
            stb_rgb_counts[stb_key]["screen_stop"] = 0
            stb_rgb_counts[stb_key]["last_rgb2"] = None
            current_time2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #stb_rgb_counts[stb_key]["last_print"] = (f"{stb_key} : 정상 부팅")
            if first_print :
                print(f"[{current_time2}] : {stb_key} : 정상 부팅")
            else : 
                pass
                              
            

        elif np.linalg.norm(np.array(rgb) - np.array(BLUE_RGB)) < 15 or np.linalg.norm(np.array(rgb) - np.array(BLACK_RGB)) < 15 :
            stb_rgb_counts[stb_key]["screen_stop"] = 0
            stb_rgb_counts[stb_key]["last_rgb2"] = None
            pass
        #####################################################################
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
        # Image 캡처
        image = capture_screen()
        # 각 STB 화면에 대해 check
        ac_check(image, STB_AC_CHECK_POSITIONS, STB_AC_OFF_TIME- 1, STB_AC_LIST)
        time.sleep(CAPTURE_INTERVAL)
        
print("***5초 후 Test 좌표 캡처 시작***")
time.sleep(5)
screenshot = capture_screen()
show_stb_positions(screenshot, STB_AC_POSITIONS, scale=0.7)
# 메모리 삭제
screenshot = None
print("3초 후 Aging Detecting Start ")
time.sleep(3)
print("Start Detecting")
time.sleep(2)
main()    
 
