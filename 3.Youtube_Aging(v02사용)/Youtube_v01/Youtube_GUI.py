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
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pip install opencv-python"])
 
'''******************경로 수정 필요******************'''

# 실행할 Python 파일 경로
script_path = os.path.join(os.path.dirname(__file__), "Youtube_방치_Aging", "Youtube.py")

'''******************경로 수정 필요******************'''

# 폴더 선택 다이얼로그
def choose_folder():
    folder_selected = filedialog.askdirectory(title="폴더 선택")
    if folder_selected:
        folder_path.set(folder_selected)  # 폴더 경로를 변수에 저장
        print(f"선택한 폴더: {folder_selected}")  # 선택된 폴더 경로 출력
    else:
        print("폴더를 선택하지 않았습니다.")

# KSTB6175_AC_aging_.py 파일 실행하는 함수
def start_check():
    STB_AGING_LIST = [stb for stb, var in stb_vars.items() if var.get()]

    if not STB_AGING_LIST:
        messagebox.showwarning("최소 1EA 이상 STB 선택")
        return
    
    # 폴더 경로 가져오기
    folder_path_value = folder_path.get()
    select_tool_value = select_tool.get()

    if not folder_path_value:
        messagebox.showwarning("폴더 경로 미지정", "폴더를 선택해 주세요.")
        return
    
    # GUI 창 닫기 
    root.destroy()

    # subprocess를 이용하여 외부 Python 스크립트 실행
    try:
        # subprocess.run을 통해 Python 스크립트 실행
        subprocess.run(
            ['python.exe', script_path, 
             '--stb_list', ','.join(map(str, STB_AGING_LIST)),  # STB 리스트를 문자열로 변환
             '--folder', folder_path_value,  # 폴더 경로 전달
             '--tool', select_tool_value,
             ],
            shell = True,
        )
        
    except Exception as e:
        messagebox.showerror("오류", f"스크립트 실행 중 오류 발생: {str(e)}")
    

# Tkinter 윈도우 설정
root = tk.Tk()
root.title("Youtube Aging 테스트")

# 창 위치 설정 (-1140, 400)
root.geometry("+{}+{}".format(0, 0))

# 1. Viewer Tool 선택
tool_label = tk.Label(root, text="1. Viewer Program 선택")
tool_label.pack(pady=5)

select_tool = tk.StringVar()  # Viewer Tool 선택 변수
tool_combobox = ttk.Combobox(root, textvariable=select_tool)
tool_combobox['values'] = ("IRIS", "SMARTVIEWER")  # 옵션 설정
tool_combobox['state'] = 'readonly'  # 읽기 전용으로 설정
tool_combobox.pack(pady=5)

# 2. STB 번호 체크박스 변수 설정
stb_label = tk.Label(root, text="2. STB 번호 선택")
stb_label.pack(pady=5)

stb_vars = {str(i): tk.BooleanVar() for i in range(1, 10)}

stb_frame = tk.Frame(root)
stb_frame.pack(pady=10)

for stb, var in stb_vars.items():
    checkbox = tk.Checkbutton(stb_frame, text=f"STB {stb}", variable=var)
    checkbox.pack(side=tk.LEFT, padx=5)

# 3. 폴더 경로를 저장할 변수
path_label = tk.Label(root, text="3. 로그 저장 경로 선택")
path_label.pack(pady=5)

folder_path = tk.StringVar()

choose_folder_button = tk.Button(root, text="경로 지정", command=choose_folder)
choose_folder_button.pack(pady=5)

folder_label = tk.Label(root, textvariable=folder_path)
folder_label.pack(pady=5)

# 4. 완료
submit_button = tk.Button(root, text="Start Youtube Check", command=start_check)
submit_button.pack(pady=5)

# Tkinter 이벤트 루프 시작
root.mainloop()
