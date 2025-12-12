import cv2
import numpy as np


class UIState:
    """
    UI에서 사용하는 모든 상태 변수들을 담는 클래스
    (global 변수를 모두 이 안에 넣어 관리)
    """
    def __init__(self):
        self.program_off = False
        self.reject_run = True
        self.yolo_run = False

        self.off_click = False
        self.reject_click = False
        self.yolo_click = False


def handle_mouse_event(event, x, y, flags, param):
    """
    마우스 클릭 / hover 이벤트 처리
    param = UIState() 객체가 전달됨
    """
    ui = param  # UI 상태 객체

    # hover 상태 체크
    if 9 < x < 84:
        ui.off_click = 48 < y < 121
        ui.reject_click = 145 < y < 218
        ui.yolo_click = 240 < y < 320
    else:
        ui.off_click = ui.reject_click = ui.yolo_click = False

    # 클릭 릴리즈 이벤트 처리
    if event == cv2.EVENT_LBUTTONUP:

        # 프로그램 종료 버튼
        if 9 < x < 84 and 48 < y < 121:
            ui.program_off = True

        # Reject ON / OFF 토글
        if 9 < x < 84 and 145 < y < 218:
            ui.reject_run = not ui.reject_run

        # YOLO Detect ON / OFF 토글
        if 9 < x < 84 and 240 < y < 320:
            ui.yolo_run = not ui.yolo_run


def draw_main_ui(ui: UIState):
    """
    UI 전체 화면(세로 메뉴 1개) 그리는 함수
    main 루프에서 매 프레임 호출하면 됨
    """
    IMG = np.zeros((470, 90, 3), np.uint8)

    # -----------------------------
    # 1) 프로그램 OFF 버튼
    # -----------------------------
    if ui.off_click:
        IMG = cv2.putText(IMG, "OFF", (15, 78), cv2.FONT_HERSHEY_DUPLEX, 1, (150,150,255), 2)
        IMG = cv2.putText(IMG, "Click here", (10,108), cv2.FONT_HERSHEY_DUPLEX, .4, (150,150,255), 1)
    else:
        IMG = cv2.putText(IMG, "OFF", (15, 80), cv2.FONT_HERSHEY_DUPLEX, 1, (250,200,255), 2)
        IMG = cv2.putText(IMG, "Click here", (10,110), cv2.FONT_HERSHEY_DUPLEX, .4, (250,200,255), 1)
    cv2.line(IMG, (5,130), (85,130), (50,50,50), 1)

    # -----------------------------
    # 2) Reject ON / OFF 버튼
    # -----------------------------
    if ui.reject_run:
        if ui.reject_click:
            IMG = cv2.putText(IMG, "ON", (20,178), cv2.FONT_HERSHEY_DUPLEX, 1, (150,150,255), 2)
            IMG = cv2.putText(IMG, "Reject on", (13,208), cv2.FONT_HERSHEY_DUPLEX, .4, (150,150,255), 1)
        else:
            IMG = cv2.putText(IMG, "ON", (20,180), cv2.FONT_HERSHEY_DUPLEX, 1, (250,200,255), 2)
            IMG = cv2.putText(IMG, "Reject on", (13,210), cv2.FONT_HERSHEY_DUPLEX, .4, (250,200,255), 1)
    else:
        if ui.reject_click:
            IMG = cv2.putText(IMG, "OFF", (15,178), cv2.FONT_HERSHEY_DUPLEX, 1, (150,150,255), 2)
            IMG = cv2.putText(IMG, "Reject off", (13,208), cv2.FONT_HERSHEY_DUPLEX, .4, (150,150,255), 1)
        else:
            IMG = cv2.putText(IMG, "OFF", (15,180), cv2.FONT_HERSHEY_DUPLEX, 1, (250,200,255), 2)
            IMG = cv2.putText(IMG, "Reject off", (13,210), cv2.FONT_HERSHEY_DUPLEX, .4, (250,200,255), 1)
    cv2.line(IMG, (5,230), (85,230), (50,50,50), 1)

    # -----------------------------
    # 3) YOLO Detect RUN / STOP 버튼
    # -----------------------------
    if ui.yolo_run:
        if ui.yolo_click:
            IMG = cv2.putText(IMG, "RUN", (15,278), cv2.FONT_HERSHEY_DUPLEX, 1, (150,150,255), 2)
            IMG = cv2.putText(IMG, "Detect on", (15,308), cv2.FONT_HERSHEY_DUPLEX, .4, (150,150,255), 1)
        else:
            IMG = cv2.putText(IMG, "RUN", (15,280), cv2.FONT_HERSHEY_DUPLEX, 1, (250,200,255), 2)
            IMG = cv2.putText(IMG, "Detect on", (15,310), cv2.FONT_HERSHEY_DUPLEX, .4, (250,200,255), 1)
    else:
        if ui.yolo_click:
            IMG = cv2.putText(IMG, "STOP", (7,278), cv2.FONT_HERSHEY_DUPLEX, 1, (150,150,255), 2)
            IMG = cv2.putText(IMG, "Detect off", (13,308), cv2.FONT_HERSHEY_DUPLEX, .4, (150,150,255), 1)
        else:
            IMG = cv2.putText(IMG, "STOP", (7,280), cv2.FONT_HERSHEY_DUPLEX, 1, (250,200,255), 2)
            IMG = cv2.putText(IMG, "Detect off", (13,310), cv2.FONT_HERSHEY_DUPLEX, .4, (250,200,255), 1)
    cv2.line(IMG, (5,330), (85,330), (50,50,50), 1)

    return IMG

