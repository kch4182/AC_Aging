import numpy as np
from PIL import ImageGrab
import time, csv, os, sys, cv2
from datetime import datetime


X_COORDINATE = int(sys.argv[4]) # 3. 각 화면에서 움직일 x축
Y_COORDINATE = int(sys.argv[6]) # 4. 각 화면에서 움직일 y축
print("X좌표:", X_COORDINATE)
print("Y좌표:", Y_COORDINATE)
#*********************************IRIS or SmartViewer Tool 적용*********************************

#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ변수 설정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
STB_POSITIONS = [
    (0, 0), (640, 0), (1280, 0),
    (0, 360), (640, 360), (1280, 360),
    (0, 720), (640, 720), (1280, 720)
]

STB_POSITIONS = [(x + X_COORDINATE, y + Y_COORDINATE) for x, y in STB_POSITIONS] # SMARTVIEWER 16:9 => 9개 layout

STB_RGB_LIST = sys.argv[2].split(',')  # list로 반환해야 함
STB_RGB_LIST = [int(STB_RGB_LIST[i])-1 for i in range(len(STB_RGB_LIST))] # List index - 1 해서 실제 값
STB_RGB_LIST_N = len(STB_RGB_LIST) # List 개수

# RGB_적용 STB 위치
STB_RGB_POSITIONS = [STB_POSITIONS[i] for i in STB_RGB_LIST]


# AC ON 기준 STB Input
STB_RGB_CHECK = STB_RGB_LIST[0]  # List[0]을 기준으로 AC Check 기준 잡음
STB_RGB_CHECK_POSITIONS = [STB_POSITIONS[STB_RGB_CHECK]]


#ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ변수 설정ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

# 1. 캡처 함수 (이미지 업데이트)
def capture_screen():
    """1920x1080 화면을 캡처하고 RGB 배열 반환"""
    screenshot = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
    return np.array(screenshot.convert("RGB"))

def rgb_check(positions, duration=6, interval=0.1):
    start_time = time.time()
    rgb_sums = {pos: np.array([0, 0, 0], dtype=np.float32) for pos in positions}
    count = 0
    
    while time.time() - start_time < duration:
        image = capture_screen()
        for x, y in positions:
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                rgb_sums[(x, y)] += image[y, x]
        count += 1
        time.sleep(interval)  # 0.1초마다 측정

    # 평균값 계산 후 정수형 튜플로 변환
    avg_rgbs = {pos: tuple(map(int, (rgb_sums[pos] / count))) for pos in positions}
    ######################################################################################
    # 평균 RGB 값을 변수에 저장
    # rgb_values = {pos: avg_rgbs[pos] for pos in avg_rgbs}# rgb_values에 저장
    rgb_values = tuple([avg_rgbs[pos] for pos in avg_rgbs])
    
    image_rgb = capture_screen()
    for i, (x, y) in enumerate(positions):
        rgb = tuple(image_rgb[y, x])

    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    print("RGB 10초 평균:",rgb_values)
    print("현재 RGB와 차이:",np.linalg.norm(np.array(rgb) - np.array(rgb_values)))
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

    ######################################################################################


    # print(avg_rgbs)  # 평균 RGB 값 출력
    return avg_rgbs

# 3. 좌표 확인용 함수
def show_stb_positions(image, positions, scale=0.5):  
    small_image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
    image_bgr = cv2.cvtColor(small_image, cv2.COLOR_RGB2BGR)
    scaled_positions = [(int(x * scale), int(y * scale)) for x, y in positions]
    for x, y in scaled_positions:
        cv2.circle(image_bgr, (x, y), 3, (0, 0, 255), -1)
    window_name = "STB Positions"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)      
    cv2.imshow(window_name, image_bgr)
    cv2.waitKey(7000)
    cv2.destroyAllWindows()

# 4. 메인 실행 함수
def main():
    while True: 
        rgb_check(STB_RGB_CHECK_POSITIONS)  # 

print("강제종료 : Ctrl + C ")
print("***3초 후 Test 좌표 캡처 시작***IRIS or SMARTVIEWER 창 전체화면 후 최상단 배치***")
time.sleep(3)
screenshot = capture_screen()
show_stb_positions(screenshot, STB_RGB_POSITIONS, scale=0.7)
print("2초 후 RGB 평균 색상 계산 시작 ")
time.sleep(2)
print("Start")
print("6초마다 RGB 평균값 계산")
print("현재 RGB와 차이 -> 0에 가까울 수록 비슷한 색상")
print("차이가 20 이하라면 정상 부팅 색상으로 확인")
main()
    
