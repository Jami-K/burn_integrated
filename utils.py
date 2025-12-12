import os
import random
import time, datetime, cv2, hid, shutil
import darknet
import numpy as np
from img_grab import Camera
from model import YOLOModel
from gap import GapAccumulator
import properties

from pypylon import pylon
from time import sleep, localtime, strftime
from multiprocessing import Process, Queue

"""비전 카메라 사용을 위한"""
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

camera = None

def burn_inspection(line, start_Q, quit_Q, reject_Q, img_Q, relay_cmd_queue):
    if line == 'A_U':
        attribute = properties.A_U
    elif line == 'B_U':
        attribute = properties.B_U
    
    run_or_stop = 'stop'
    reject_or_pass = 'reject'
    del_folder(properties.day_limit)

    """ 카메라 활성 """
    vision_CAM = Camera(camera_ip = attribute['camera_ip'],
                        camera_setting = attribute['camera_setting'],
                        camera_mode = attribute['camera_mode']
                        )
    cam, converter = vision_CAM.load_camera()

    if cam:
        null_image = np.zeros((494,659,3),np.uint8)  # 빈 이미지 1280 1024
        null_image = cv2.putText(null_image, "Waiting RUN signal...", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, [255,200,255], 2)
        
        """ YOLO 모델 활성 """
        model = YOLOModel(config_file = attribute['config_file'],
                          data_file = attribute['data_file'],
                          weights = attribute['weights']
                          )

        """ 본 검사 프로그램 가동 """
        while True:
            if start_Q.qsize() > 0: # 검사 가동상태 변경
                run_or_stop = start_Q.get()
            
            if quit_Q.qsize() > 0:
                cmd = quit_Q.get()
                if cmd == 'off':
                    break
            
            if reject_Q.qsize() > 0: # 리젝트 유무 설정
                reject_or_pass = reject_Q.get()
            
            # 오늘 날짜의 이미지 저장경로 생성
            save_dir = create_folder(line)
            
            if run_or_stop == 'start':
                image_raw, image_rgb, grabResult, grab_on = vision_CAM.get_img(null_image)
            
                if grab_on == 2: # YOLO모델 가동
                    detections, image_resized = model.predict(image_rgb)
                    img_Q.put(cv2.resize(image_resized, (350, 350), interpolation=cv2.INTER_LINEAR))
                
                    if detections:
                        for result in detections:
                            label, confidence, (x, y, w, h) = result
                            if label == '1' and confidence > attribute['save_limit']: # 저장 기준을 넘겼음
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                name_save = f"{line}_{timestamp}.jpg"
                                cv2.imwrite(os.path.join(save_dir, name_save), image_rgb)
                                print(f"[Saved] >>>>>>>> {name_save}")
                                
                                if confidence >= attribute['reject_limit']: # 리젝트 기준을 넘겼음
                                    relay_cmd_queue.put(("NG", attribute['relay_port'], attribute['delay'], attribute['duration']))
                                    print(f"[{line}] >>>>>>>> {label}, {confidence}")
                                
                else: # 카메라로부터 이미지를 받지 못하였다면
                    n_image = np.zeros((494,659,3),np.uint8)
                    n_image = cv2.putText(n_image, "Camera Err...", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, [255,200,255], 2)
                    img_Q.put(n_image)
            else: #프로그램 시작하지 않은 상태라면
                img_Q.put(null_image)
            
        vision_CAM.destroy_cam()
        cv2.destroyAllWindows()
        return

def gap_inspection(line, start_Q, quit_Q, reject_Q, img_Q, relay_cmd_queue):
    if line == 'A_D':
        attribute = properties.A_D
    elif line == 'B_D':
        attribute = properties.B_D
    
    run_or_stop = 'stop'
    reject_or_pass = 'reject'
    del_folder(properties.day_limit)

    """ 카메라 활성 """
    vision_CAM = Camera(camera_ip = attribute['camera_ip'],
                        camera_setting = attribute['camera_setting'],
                        camera_mode = attribute['camera_mode']
                        )
    cam, converter = vision_CAM.load_camera()

    if cam:
        null_image = np.zeros((494,659,3),np.uint8)  # 빈 이미지
        null_image = cv2.putText(null_image, "Waiting RUN signal...", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, [255,200,255], 2)
        loaded_view = np.zeros((494,659,3),np.uint8)  # 빈 이미지
        
        """ YOLO 모델 활성 """
        model = YOLOModel(config_file = attribute['config_file'],
                          data_file = attribute['data_file'],
                          weights = attribute['weights']
                          )
        
        """ Gap 화면 구성 활성 """
        gap_accumulator = GapAccumulator(crop_x_start = attribute['crop_x_start'],
                                         crop_x_end = attribute['crop_x_end'],
                                         crop_y_start = attribute['crop_y_start'],
                                         crop_y_end = attribute['crop_y_end'],
                                         max_segments = attribute['max_segments'],
                                         )

        """ 본 검사 프로그램 가동 """
        while True:
            if start_Q.qsize() > 0:
                run_or_stop = start_Q.get()
                #print("검사 가동 상태를 변경합니다.")
            
            if quit_Q.qsize() > 0:
                cmd = quit_Q.get()
                if cmd == 'off':
                    break
                    
            if reject_Q.qsize() > 0:
                reject_or_pass = reject_Q.get()
                #print("리젝트 유무 설정을 변경합니다.")
            
            # 오늘 날짜의 이미지 저장경로 생성
            save_dir = create_folder(line)
            
            if run_or_stop == 'start':
                image_raw, image_rgb, grabResult, grab_on = vision_CAM.get_img(null_image)
            
                if grab_on == 2:
                    image_raw = cv2.flip(image_raw, 0) # B기 위치보정
                    
                    detections, image_resized = model.predict(image_raw,
                                                              orig_width = image_raw.shape[1],
                                                              orig_height = image_raw.shape[0]
                                                              )
                    
                    # Gap 화면 구현
                    view, view_highlighted = gap_accumulator.update(image_raw, detections)
                    if view is not None:
                        loaded_view = view
                    
                    if detections:
                        for result in detections:
                            label, confidence, (x, y, w, h) = result
                            if label == '1' and confidence > attribute['save_limit']: # 저장 기준을 넘겼음
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                name_save = f"{line}_{timestamp}.jpg"
                                cv2.imwrite(os.path.join(save_dir, name_save), image_rgb)
                                print(f"[Saved] >>>>>>>> {name_save}")
                                
                                if confidence >= attribute['reject_limit']: # 리젝트 기준을 넘겼음
                                    relay_cmd_queue.put(("NG", attribute['relay_port'], attribute['delay'], attribute['duration']))
                                    print(f"[{line}] >>>>>>>> {label}, {confidence}")

                    img_Q.put(loaded_view)
                                
                #else: # 카메라로부터 이미지를 받지 못하였다면
                #    n_image = np.zeros((494,659,3),np.uint8)
                #    n_image = cv2.putText(n_image, "Camera Err...", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 1, [255,200,255], 2)
                #    img_Q.put(n_image)
            else: #프로그램 시작하지 않은 상태라면
                img_Q.put(loaded_view)
                
        vision_CAM.destroy_cam()
        cv2.destroyAllWindows()
        return

def create_folder(line): # 오늘 날짜(YYYY-MM-DD) 폴더명 생성
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    save_dir = os.path.join("./reject_img", today, line)
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def del_folder(day_limit):
    base_dir = "./reject_img"

    if not os.path.exists(base_dir):
        print(f"폴더가 존재하지 않습니다: {base_dir}")
        return
    days = os.listdir(base_dir)
   
    day_nums = []  # 날짜 폴더만 골라서 YYYYMMDD 정수로 변환
    for day in days:
        try:
            num = int(day.replace("-", ""))  # "2025-01-15" → 20250115
            day_nums.append(num)
        except ValueError:
            continue

    day_nums.sort()

    if len(day_nums) > day_limit:
        del_count = len(day_nums) - day_limit
        del_list = day_nums[:del_count]  # 오래된 날짜 순 삭제
        for num in del_list:
            folder_name = f"{str(num)[:4]}-{str(num)[4:6]}-{str(num)[6:]}"
            folder_path = os.path.join(base_dir, folder_name)

            print(f"{folder_name} 폴더를 삭제합니다.")
            shutil.rmtree(folder_path)
    else:
        print("-" * 40)
        print(f"{day_limit}일 이하라 삭제할 폴더가 없습니다.")
        print("-" * 40)

def get_latest(q):
    """    Queue 내부의 모든 데이터를 비우고
                      마지막(최신) 항목만 반환한다.
           Queue가 비어 있으면 None 반환.    """
    latest = None
    try:
        while True:
            latest = q.get_nowait()
    except:
        pass
    return latest
