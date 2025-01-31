import numpy as np
from PIL import ImageGrab
import time, csv, os, sys, cv2
from datetime import datetime

#************STB Model 설정************
AC_AGING_IRIS = tuple(map(int, sys.argv[14].strip("()").split(", ")))
AC_AGING_SMART = tuple(map(int, sys.argv[16].strip("()").split(", ")))
CAPTURE_INTERVAL = 0.3

MOVE_IRIS = tuple(map(int, sys.argv[18].strip("()").split(", ")))
MOVE_SMART = tuple(map(int, sys.argv[20].strip("()").split(", ")))

select_tool_value = str(sys.argv[12])
BLUE_RGB_IRIS = (10, 4, 240)
BLUE_RGB_SMART = (8, 8, 252)
BLACK_RGB = (12, 12, 12)

if select_tool_value == "IRIS":
    BLUE_RGB = BLUE_RGB_IRIS
    AC_AGING = AC_AGING_IRIS
    x_move, y_move = MOVE_IRIS
else:
    BLUE_RGB = BLUE_RGB_SMART
    AC_AGING = AC_AGING_SMART
    x_move, y_move = MOVE_SMART

STB_POSITIONS = [
    (x + x_move, y + y_move)
    for x, y in [(0, 0), (640, 0), (1280, 0), (0, 360), (640, 360), (1280, 360), (0, 720), (640, 720), (1280, 720)]
]
STB_AC_LIST = [int(ac) - 1 for ac in sys.argv[2].split(',')]
STB_AC_LIST_N = len(STB_AC_LIST)
STB_AC_POSITIONS = [STB_POSITIONS[ac] for ac in STB_AC_LIST]

STB_AC_ON_TIME = int(sys.argv[4])
STB_AC_OFF_TIME = int(sys.argv[6])
STB_AC_CHECK_TIME = int(sys.argv[8])

STB_AC_CHECK = STB_AC_LIST[0]
STB_AC_CHECK_POSITIONS = [STB_POSITIONS[STB_AC_CHECK]]

log_path = sys.argv[10]
START_DAY = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
last_hour_logged = -10
start_time = None
stb_log_status = {f"STB {STB_AC_LIST[i]+1}": {"start_time": None} for i in range(len(STB_AC_LIST))}
stb_rgb_counts = {
    f"STB {i+1}": {"screen_black": 0,"screen_blue":0,"screen_stop":0, "last_rgb": None, "black_count" :0, "last_rgb2": None} for i in range(len(STB_POSITIONS))
}
print(f"Configured with tool: {select_tool_value}, On Time: {STB_AC_ON_TIME}, Off Time: {STB_AC_OFF_TIME}")
print(f"STB AC List: {STB_AC_LIST}")
print("Initialization complete.")


# Functions
def capture_screen():
    try:
        screenshot = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
        return np.array(screenshot.convert("RGB"))
    except Exception as e:
        print(f"Error in capture_screen: {e}")
        return None

def show_stb_positions(image, positions, scale=0.5):
    try:
        small_image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        image_bgr = cv2.cvtColor(small_image, cv2.COLOR_RGB2BGR)
        scaled_positions = [(int(x * scale), int(y * scale)) for x, y in positions]
        for x, y in scaled_positions:
            cv2.circle(image_bgr, (x, y), 3, (0, 0, 255), -1)
        cv2.imshow("STB Positions", image_bgr)
        cv2.waitKey(7000)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error in show_stb_positions: {e}")

def log_event(stb_key, event, already_flag):
    compare_log = ["stb :", stb_key, "time : ", current_time, "event :", event ]
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        current_time2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(log_path, f"{START_DAY}.csv")
        
        print("111111.여기가 already_flag : ",already_flag)

        print("222222.여기가 compare_log : ",compare_log)

        if already_flag != compare_log :  # 이미 기록된 시간과 같으면 기록 안함
            print(f"[{current_time}] {stb_key}: {event}")
            os.makedirs(log_path, exist_ok=True)
            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([stb_key, current_time2, event])

        already_flag = compare_log # 기록 후 flag 갱신    
        return already_flag
            
    except Exception as e:
        print(f"Error in log_event: {e}")

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
                        for _ in range(10):
                            # 캡처 화면 update
                            image_check = capture_screen()
                            error_check(image_check, STB_AC_POSITIONS, stb_log_status)
                        start_time = None
                        break

        # BLUE_RGB_IRIS 상태가 지속되지 않는다면 start_time 초기화                
        elif start_time is not None:
            start_time = None  # IRIS 상태가 끊어지면 start_time 초기화

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡMain 함수ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ    

# Error Check 함수
def error_check(image, positions, stb_log_status):
    global stb_rgb_counts
    for i, (x, y) in enumerate(positions):
        rgb = tuple(image[y, x])
        stb_key = f"STB {STB_AC_LIST[i]+1}"
        # 중복 IF문 진입 방지
        already_flag = stb_log_status[stb_key].get("last_log", None)
        print("0000000.여기가 already_flag : ",already_flag)
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

# Main loop
def main():
    print("Starting detection...")
    time.sleep(5)
    screenshot = capture_screen()
    if screenshot is not None:
        show_stb_positions(screenshot, STB_AC_POSITIONS, scale=0.7)
    else:
        print("Error: Unable to capture initial screenshot. Exiting.")
        return

    while True:
        try:
            image = capture_screen()
            if image is not None:
                ac_check(image, STB_AC_CHECK_POSITIONS, STB_AC_OFF_TIME - 1, STB_AC_LIST)
            else:
                print("Error: Unable to capture screen during loop.")
            time.sleep(CAPTURE_INTERVAL)
        except KeyboardInterrupt:
            print("Program terminated by user.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
