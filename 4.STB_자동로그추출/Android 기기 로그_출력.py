# Android_STB Exo_Player 로그 추출
import os
import subprocess
from datetime import datetime


GBOARD_IME = "com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME"


def run_adb(args, **kwargs):
    try:
        return subprocess.run(["adb", *args], text=True, **kwargs)
    except FileNotFoundError:
        print("adb를 찾을 수 없습니다. Android platform-tools가 PATH에 등록되어 있는지 확인하세요.")
        raise SystemExit(1)


def get_adb_devices():
    result = run_adb(["devices"], capture_output=True, check=True)
    devices = []

    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices.append({"serial": parts[0], "state": parts[1]})

    return devices


def is_usb_serial(serial):
    return ":" not in serial and not serial.startswith("emulator-")


def normalize_tcp_target(ipv4):
    return ipv4 if ":" in ipv4 else f"{ipv4}:5555"


def choose_usb_device(usb_devices):
    if len(usb_devices) == 1:
        return usb_devices[0]["serial"]

    print("사용 가능한 USB 디바이스가 여러 개입니다.")
    for index, device in enumerate(usb_devices, start=1):
        print(f"{index}. {device['serial']}")

    while True:
        selected = input("사용할 USB 디바이스 번호 입력 : ").strip()
        if selected.isdigit() and 1 <= int(selected) <= len(usb_devices):
            return usb_devices[int(selected) - 1]["serial"]
        print("목록에 있는 번호를 입력하세요.")


def find_usb_device():
    devices = get_adb_devices()
    usable_usb_devices = [
        device
        for device in devices
        if device["state"] == "device" and is_usb_serial(device["serial"])
    ]

    if usable_usb_devices:
        serial = choose_usb_device(usable_usb_devices)
        print(f"USB 연결 디바이스 사용: {serial}")
        return serial

    blocked_usb_devices = [
        device for device in devices if device["state"] != "device" and is_usb_serial(device["serial"])
    ]
    if blocked_usb_devices:
        print("USB 디바이스가 보이지만 사용할 수 있는 상태가 아닙니다.")
        for device in blocked_usb_devices:
            print(f"- {device['serial']} ({device['state']})")
        print("unauthorized 상태라면 Android 화면에서 USB 디버깅 RSA 허용을 눌러야 합니다.")

    return None


def connect_wireless_device():
    while True:
        ipv4 = input("STB IPV4 입력 : ").strip()
        if ipv4.lower() in ("q", "quit", "exit"):
            raise SystemExit(0)
        if not ipv4:
            print("IP를 입력하세요. 종료하려면 q를 입력하세요.")
            continue

        target = normalize_tcp_target(ipv4)
        result = run_adb(["connect", target], capture_output=True)
        output = "\n".join(
            text.strip() for text in (result.stdout, result.stderr) if text and text.strip()
        )

        if output:
            print(output)

        devices = get_adb_devices()
        connected = any(
            device["serial"] == target and device["state"] == "device" for device in devices
        )

        if result.returncode == 0 and connected:
            print(f"무선 연결 디바이스 사용: {target}")
            return target

        print("무선 ADB 연결 실패")
        print("USB 없이 무선으로 붙으려면 STB의 5555 포트가 열려 있어야 합니다.")
        print("USB 연결 상태에서 한 번 `adb tcpip 5555`를 실행해야 하는 기기도 있습니다.")


def connect_stb():
    serial = find_usb_device()
    if serial:
        return serial

    print("사용 가능한 USB 디바이스가 없어 무선 연결을 시도합니다.")
    return connect_wireless_device()


def set_gboard_keyboard(serial):
    result = run_adb(
        ["-s", serial, "shell", "ime", "set", GBOARD_IME],
        capture_output=True,
    )

    if result.returncode != 0:
        print("Gboard Keyboard 변경 실패. 로그 추출은 계속 진행합니다.")
        if result.stderr:
            print(result.stderr.strip())


def log_check(serial):
    log_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

    # 바탕화면에 Log 폴더 생성
    log_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Log")
    os.makedirs(log_folder, exist_ok=True)

    # 로그 파일 경로 설정
    log_save_path = os.path.join(log_folder, log_filename)

    try:
        print("로그 추출 중...")
        with open(log_save_path, "w", encoding="utf-8") as log_file:
            run_adb(
                ["-s", serial, "logcat", "-d", "-v", "threadtime"],
                stdout=log_file,
                check=True,
            )
            #run_adb(
            #    ["-s", serial, "logcat", "-d", "-v", "threadtime"],
            #    stdout=log_file,
            #    check=True,
            #)

        print("로그 저장 완료")
        print("로그 저장 명 : ", log_save_path)
        set_gboard_keyboard(serial)
    except subprocess.CalledProcessError as e:
        print("로그 추출 실패:", e)
        set_gboard_keyboard(serial)


def main():
    print("STB 연결 실패 or 정상 작동하지 않아 키보드가 뜨지 않는다면 구글 설정에서 Gboard Keyboard로 변경해야 함")
    serial = connect_stb()
    set_gboard_keyboard(serial)
    log_check(serial)
    os.system("pause")


if __name__ == "__main__":
    main()
