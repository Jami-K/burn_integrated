import cv2
import numpy as np
import time

class GapAccumulator:
    def __init__(self,
                 crop_x_start=320, crop_x_end=360,
                 crop_y_start=0, crop_y_end=None,
                 max_segments=30, interval_sec=0.001, target_label=1):
        self.crop_x_start = crop_x_start
        self.crop_x_end = crop_x_end
        self.crop_y_start = crop_y_start
        self.crop_y_end = crop_y_end  # None이면 전체 높이
        self.crop_width = crop_x_end - crop_x_start
        self.max_segments = max_segments
        self.interval_sec = interval_sec
        self.target_label = target_label
        self.last_time = time.time()

        # crop 높이 계산 (frame 입력 후 갱신될 수 있음)
        self.segment_height = None
        self.view_height = None

        self.initialized = False

        # 버퍼 초기화
        self.view_buffer = None
        self.view_highlight_buffer = None

    def initialize_buffers(self, frame):
        """첫 프레임에서 이미지 크기 기준으로 버퍼 초기화"""
        y_end = self.crop_y_end if self.crop_y_end is not None else frame.shape[0]
        self.segment_height = y_end - self.crop_y_start
        self.view_height = self.segment_height * self.max_segments

        self.view_buffer = np.zeros((self.view_height, self.crop_width, 3), dtype=np.uint8)
        self.view_highlight_buffer = np.zeros_like(self.view_buffer)
        self.initialized = True

    def update(self, frame, detection=None):
        current_time = time.time()
        if current_time - self.last_time < self.interval_sec:
            return None, None

        self.last_time = current_time

        if not self.initialized:
            self.initialize_buffers(frame)

        y_end = self.crop_y_end if self.crop_y_end is not None else frame.shape[0]

        # 감지 여부 확인
        detected = False
        frame_highlighted = frame.copy()

        if detection is not None:
            for det in detection:
                x1, y1, x2, y2, conf, cls = det
                if int(cls) == self.target_label:
                    detected = True
                    cv2.rectangle(frame_highlighted, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

        cropped = frame[self.crop_y_start:y_end, self.crop_x_start:self.crop_x_end]
        cropped_highlighted = frame_highlighted[self.crop_y_start:y_end, self.crop_x_start:self.crop_x_end]
        
        h, w, _ = cropped.shape
        if h != self.segment_height or w != self.crop_width:
            cropped = cv2.resize(cropped, (self.crop_width, self.segment_height))
            cropped_highlighted = cv2.resize(cropped_highlighted, (self.crop_width, self.segment_height))

        # === 스크롤 방식으로 이미지 누적 (vstack 대체) ===
        shift = self.segment_height  # +로 바꿔서 아래로 밀기
        self.view_buffer = np.roll(self.view_buffer, shift, axis=0)
        self.view_highlight_buffer = np.roll(self.view_highlight_buffer, shift, axis=0)
        
        self.view_buffer[:self.segment_height, :, :] = cropped
        self.view_highlight_buffer[:self.segment_height, :, :] = cropped_highlighted

        return self.view_buffer, self.view_highlight_buffer

"""
import cv2
import numpy as np
import time

class GapAccumulator:
    def __init__(self,
                 crop_x_start=320, crop_x_end=360,
                 crop_y_start=0, crop_y_end=None,
                 max_segments=30, interval_sec=0.001, target_label=1):
        self.crop_x_start = crop_x_start
        self.crop_x_end = crop_x_end
        self.crop_y_start = crop_y_start
        self.crop_y_end = crop_y_end  # None이면 전체 높이
        self.crop_width = crop_x_end - crop_x_start
        self.max_segments = max_segments
        self.interval_sec = interval_sec
        self.target_label = target_label
        self.segments, self.segments_highlighted = [], []
        self.flags = []  # segment마다 감지 여부 (True/False)
        self.last_time = time.time()

    def update(self, frame, detection=None):
        current_time = time.time()
        if current_time - self.last_time < self.interval_sec:
            return None, None

        self.last_time = current_time

        y_end = self.crop_y_end if self.crop_y_end is not None else frame.shape[0]

        # 감지 여부 확인
        detected = False
        frame_highlighted = frame.copy()

        if detection is not None:
            for det in detection:
                x1, y1, x2, y2, conf, cls = det
                # crop 영역과 겹치는지 확인
                #if (x2 < self.crop_x_start or x1 > self.crop_x_end or
                #    y2 < self.crop_y_start or y1 > y_end):
                #    continue
                if int(cls) == self.target_label:
                    detected = True
                    cv2.rectangle(frame_highlighted, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
        
        cropped = frame[self.crop_y_start:y_end, self.crop_x_start:self.crop_x_end]
        cropped_highlighted = frame_highlighted[self.crop_y_start:y_end, self.crop_x_start:self.crop_x_end]
                    
        self.segments.append(cropped)
        self.segments_highlighted.append(cropped_highlighted)
        self.flags.append(detected)

        # 오래된 항목 삭제
        if len(self.segments) > self.max_segments:
            self.segments.pop(0)
            self.flags.pop(0)

        # 누적 이미지 생성 (세로 방향)
        view = np.vstack(self.segments[::-1]).copy()
        view_highlighted = np.vstack(self.segments_highlighted[::-1]).copy()

        return view, view_highlighted
"""
