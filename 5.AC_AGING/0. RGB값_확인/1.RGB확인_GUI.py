import subprocess, sys, os, time
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

# Pakage 설치
try:
    import PIL 
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    print("pillow 설치 성공")
try :
    import numpy as np
except ImportError :
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    print("numpy 설치 성공")
try :
    import cv2
except ImportError :
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])


# 실행할 Python 파일 경로
script_path = os.path.join(os.path.dirname(__file__), "RGB확인", "RGB확인.py")


# KSTB6175_AC_aging_.py 파일 실행하는 함수
def start_rgb_check():
    STB_AC_LIST = [stb for stb, var in stb_vars.items() if var.get()]

    if not STB_AC_LIST:
        messagebox.showwarning("최소 1EA 이상 STB 선택")
        return

    X_COORDINATE = int(x_coordinate.get())
    Y_COORDINATE = int(y_coordinate.get())
    # 폴더 경로 가져오기
    

    # GUI 창 닫기 
    root.destroy()

    # subprocess를 이용하여 외부 Python 스크립트 실행
    try:
        # subprocess.run을 통해 Python 스크립트 실행
        subprocess.run(
            ['python.exe', script_path, 
             '--stb_list', ','.join(map(str, STB_AC_LIST)),  # STB 리스트를 문자열로 변환
             '--X_coordinate', str(X_COORDINATE), 
             '--Y_coordinate', str(Y_COORDINATE), 
             ],
            shell = True,
        )
        
    except Exception as e:
        messagebox.showerror("오류", f"스크립트 실행 중 오류 발생: {str(e)}")

# Tkinter 윈도우 설정
root = tk.Tk()
root.title("RGB 평균 출력")

# 창 위치 설정 (-1140, 400)
root.geometry("+{}+{}".format(0, 0))


# 1. STB 번호 체크박스 변수 설정
stb_label = tk.Label(root, text="1. RGB 추출할 STB 번호 선택")
stb_label.pack(pady=5)

stb_vars = {str(i): tk.BooleanVar() for i in range(1, 10)}

stb_frame = tk.Frame(root)
stb_frame.pack(pady=10)

for stb, var in stb_vars.items():
    checkbox = tk.Checkbutton(stb_frame, text=f"STB {stb}", variable=var)
    checkbox.pack(side=tk.LEFT, padx=5)

# 2. STB X좌표
tk.Label(root, text="X좌표").pack(pady=5)
x_coordinate = tk.Entry(root)
x_coordinate.insert(0, "500")
x_coordinate.pack(pady=5)

# 3. STB Y좌표
tk.Label(root, text="Y좌표").pack(pady=5)
y_coordinate = tk.Entry(root)
y_coordinate.insert(0, "300")
y_coordinate.pack(pady=5)



# 4. 제출 버튼
submit_button = tk.Button(root, text="Start", command=start_rgb_check)
submit_button.pack(pady=20)

# Tkinter 이벤트 루프 시작
root.mainloop()
