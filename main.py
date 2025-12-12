import utils
import relay
import ui
import time, cv2, psutil
import numpy as np
from multiprocessing import Process, Queue

# AB측 Queue 정의 (가동, 종료, 리젝트신호, 이미지, 셋팅값)
AU_start, AU_quit, AU_reject, AU_img = Queue(), Queue(), Queue(), Queue()
AD_start, AD_quit, AD_reject, AD_img = Queue(), Queue(), Queue(), Queue()

BU_start, BU_quit, BU_reject, BU_img = Queue(), Queue(), Queue(), Queue()
BD_start, BD_quit, BD_reject, BD_img = Queue(), Queue(), Queue(), Queue()

relay_cmd_queue = Queue()

if __name__ == "__main__":
    Check = []
    
    for process in psutil.process_iter():
        if 'python' in process.name():
            Check.append(str(process.pid))
    
    if len(Check) == 1:
        
        p_Relay = Process(target=relay.RelayController, args=(relay_cmd_queue,))
        p_Relay.start(); time.sleep(0.5)

        p_AU = Process(target=utils.burn_inspection, args=('A_U', AU_start, AU_quit, AU_reject, AU_img,relay_cmd_queue,))
        p_BU = Process(target=utils.burn_inspection, args=('B_U', BU_start, BU_quit, BU_reject, BU_img,relay_cmd_queue,))
        
        p_AD = Process(target=utils.gap_inspection, args=('A_D', AD_start, AD_quit, AD_reject, AD_img,relay_cmd_queue,))
        p_BD = Process(target=utils.gap_inspection, args=('B_D', BD_start, BD_quit, BD_reject, BD_img,relay_cmd_queue,))

        p_AU.start(); time.sleep(1)
        p_AD.start(); time.sleep(1)
        p_BU.start(); time.sleep(1)
        p_BD.start(); time.sleep(1)

        cv2.namedWindow('Noksan', flags=cv2.WINDOW_NORMAL)
        ui_state = ui.UIState()
        cv2.setMouseCallback("Noksan", ui.handle_mouse_event, ui_state)
        cv2.resizeWindow(winname='Noksan', width=200, height=800)
    
        while True:
            img = ui.draw_main_ui(ui_state)
            cv2.imshow('Noksan', img)
            cv2.moveWindow('Noksan', 10, 0)
            cv2.waitKey(1)
            
            imgAU = utils.get_latest(AU_img)
            if imgAU is not None:
                cv2.imshow('A-Upper', imgAU)
                cv2.moveWindow('A-Upper', 175, 50)

            imgAD = utils.get_latest(AD_img)
            if imgAD is not None:
                cv2.imshow('A-Down', imgAD)
                cv2.moveWindow('A-Down', 175, 500)
        
            imgBU = utils.get_latest(BU_img)
            if imgBU is not None:
                cv2.imshow('B-Upper', imgBU)
                cv2.moveWindow('B-Upper', 575, 50)

            imgBD = utils.get_latest(BD_img)
            if imgBD is not None:
                cv2.imshow('B-Down', imgBD)
                cv2.moveWindow('B-Down', 575, 500)
        
            if ui_state.program_off:
                AU_quit.put('off'); AD_quit.put('off');  BU_quit.put('off'); BD_quit.put('off')
                p_AU.join(timeout=2); p_AD.join(timeout=2); p_BU.join(timeout=2); p_BD.join(timeout=2)
                
                for p in (p_AU, p_AD, p_BU, p_BD):
                    if p.is_alive():
                        p.terminate(); p.join()
                        
                relay_cmd_queue.put(('EXIT', None, None, None))
                p_Relay.join(timeout=3)
                
                if p_Relay.is_alive():
                    p_Relay.terminate(); p_Relay.join()
                cv2.destroyAllWindows()
                break

        print("프로그램 종료")
        time.sleep(2)
        
    else:
        print("중복 실행 중입니다.\n")
        print("다른 python 프로그램을 종료해주세요")
        time.sleep(2)
