import tkinter as tk
from tkinter import messagebox

# 색상 미리보기를 업데이트하는 함수
def update_color_preview():
    try:
        # R, G, B 값 가져오기
        r = int(r_entry.get())
        g = int(g_entry.get())
        b = int(b_entry.get())
        
        # 값이 0~255 범위 내에 있는지 확인
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            # 색상 미리보기 업데이트
            color_preview.config(bg=f"#{r:02x}{g:02x}{b:02x}")
            rgb_value_label.config(text=f"RGB: ({r}, {g}, {b})")  # RGB 값 표시
        else:
            messagebox.showwarning("잘못된 입력", "R, G, B 값은 0부터 255 사이여야 합니다.")
    except ValueError:
        messagebox.showwarning("잘못된 입력", "R, G, B 값은 숫자여야 합니다.")

# Tkinter 윈도우 설정
root = tk.Tk()
root.title("RGB 값 입력")

# 창 위치 및 크기 설정
root.geometry("300x400")
root.resizable(False, False)

# 기본 스타일 설정 (font, padding)
label_font = ("Arial", 12)
entry_font = ("Arial", 12)
button_font = ("Arial", 12, "bold")

# 레이아웃 설정 (grid를 사용하여 위젯 배치)
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(expand=True, fill=tk.BOTH)

# 1. R, G, B 값 입력 레이블 및 입력 필드
tk.Label(main_frame, text="R (0~255) ", font=label_font).grid(row=0, column=0, pady=5, sticky="w")
r_entry = tk.Entry(main_frame, font=entry_font)
r_entry.grid(row=0, column=1, pady=5)

tk.Label(main_frame, text="G (0~255) ", font=label_font).grid(row=1, column=0, pady=5, sticky="w")
g_entry = tk.Entry(main_frame, font=entry_font)
g_entry.grid(row=1, column=1, pady=5)

tk.Label(main_frame, text="B (0~255) ", font=label_font).grid(row=2, column=0, pady=5, sticky="w")
b_entry = tk.Entry(main_frame, font=entry_font)
b_entry.grid(row=2, column=1, pady=5)

# 2. 색상 업데이트 버튼
update_button = tk.Button(main_frame, text="색상 업데이트", command=update_color_preview, font=button_font, bg="white", fg="black")
update_button.grid(row=5, columnspan=2, pady=10)

# 3. 색상 미리보기 프레임
color_preview_frame = tk.Frame(main_frame)
color_preview_frame.grid(row=3, columnspan=2, pady=20)

color_preview_label = tk.Label(color_preview_frame, text="색상 미리보기", font=("Arial", 14, "bold"))
color_preview_label.grid(row=0, column=0, pady=5)

color_preview = tk.Label(color_preview_frame, width=20, height=5, relief="solid", bg="#000000")
color_preview.grid(row=1, column=0, pady=5)

# RGB 값 표시 레이블
rgb_value_label = tk.Label(main_frame, text="RGB: (0, 0, 0)", font=("Arial", 12, "italic"))
rgb_value_label.grid(row=4, columnspan=2, pady=10)



# Tkinter 이벤트 루프 시작
root.mainloop()
