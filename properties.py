'''
====================================================
공통 속성값 설정
====================================================
'''
# choose 'cam' or 'vision_cam'
cam_type = 'vision_cam'

# if U press q key, close program
esc = 114

# cv2.waitKey
frame_delay = 1

"""각종 설정 값"""
relay_port = 0 #USB-Relay포트
Reject_limit = 95 #리젝트 한계 기준
Save_img_limit = 0.85 #이미지 저장 한계 기준
relay_runtime = 0.15

"""데이터 저장 일수"""
day_limit = 183

'''NG 이미지 창 x 죄표'''
small_x = int(int(659 * .8) * 2 + 30 + 90 + 20 + 20)

'''
====================================================
카메라별/위치별 속성값 설정
====================================================
'''

A_U = {
    'line': 'A',
    'window': '#12A.Line_Upper - Q : Quit',
    'camera_ip': '192.168.30.1',
    'camera_setting': '/home/nongshim/Project/burn_integrated/camera/12A_BURN_UP.pfs',
    'camera_mode' : 'TRIGGER',
    'relay_port': 1,
    'delay': 0.17,
    'duration': 0.03,
    "config_file": './data/yolov4_UP.cfg',
    "data_file": './data/obj_UP.data',
    "weights": './weights/UP/240124_9000.weights',
    'reject_limit': 0.95,
    'save_limit': 0.80
    }

A_D = {
    'line': 'A',
    'window': '#12A.Line_Down - Q : Quit',
    'camera_ip': '192.168.100.1',
    'camera_setting': './camera_setting_AD.pfs',
    'camera_mode': 'VIDEO',
    'crop_x_start':0,
    'crop_x_end':1200,
    'crop_y_start':50,
    'crop_y_end':250,
    'max_segments':20,
    'relay_port': 2,
    'delay': 0.17,
    'duration': 0.03,
    "config_file": './data/yolov4_DOWN.cfg',
    "data_file": './data/obj_DOWN.data',
    "weights": './weights/240124_9000.weights'
}

B_U = {
    'line': 'B',
    'window': '#12B.Line_Upper - Q : Quit',
    'camera_ip': '192.168.80.1',
    'camera_setting': '/home/nongshim/Project/burn_integrated/camera/12B_BURN_UP.pfs',
    'camera_mode': 'TRIGGER',
    'relay_port': 3,
    'delay': 0.17,
    'duration': 0.03,
    "config_file": './data/yolov4_UP.cfg',
    "data_file": './data/obj_UP.data',
    "weights": './weights/240124_9000.weights'
    }

B_D = {
    'line': 'B',
    'window': '#12B.Line_Down - Q : Quit',
    'camera_ip': '192.168.50.1',
    'camera_setting': '/home/nongshim/Project/burn_integrated/camera/12B_BURN_DOWN.pfs',
    'camera_mode': 'VIDEO',
    'crop_x_start':0,
    'crop_x_end':1200,
    'crop_y_start':50,
    'crop_y_end':250,
    'max_segments':20,
    'relay_port': 4,
    'delay': 0.17,
    'duration': 0.03,
    "config_file": './data/yolov4_DOWN.cfg',
    "data_file": './data/obj_DOWN.data',
    "weights": './weights/DOWN/yolov4_5000_251031.weights'
}


if __name__ == "__main__":
    print("불러오고 싶은 라인의 번호를 입력해주세요.")
