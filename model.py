import cv2
import random
import darknet

class YOLOModel:
    def __init__(self, config_file, data_file, weights, thresh=0.25, nms=0.45):
        """
        YOLO 모델 초기화
        """
        random.seed(3)  # 박스 색상 고정
        self.network, self.class_names, self.class_colors = darknet.load_network(
            config_file=config_file,
            data_file=data_file,
            weights=weights,
            batch_size=1
        )
        self.width = darknet.network_width(self.network)
        self.height = darknet.network_height(self.network)
        self.thresh = thresh
        self.nms = nms

    def predict(self, frame, orig_width=None, orig_height=None):
        """
                이미지(frame)에서 객체 검출 수행
        return: detections(list), image_resized(np.ndarray)
        detections: [(x1, y1, x2, y2, conf, cls), ...]
        """
        darknet_image = darknet.make_image(self.width, self.height, 3)

        # 전처리
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (self.width, self.height), interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())

        # 추론
        detections = darknet.detect_image(
            self.network,
            self.class_names,
            darknet_image,
            thresh=self.thresh,
            nms=self.nms
        )
        darknet.free_image(darknet_image)

        # detections = [(label, confidence, (x, y, w, h)), ...]
        # → gap.py에 맞게 변환 (x1, y1, x2, y2, conf, cls)
        results = []
        for label, conf, bbox in detections:
            x, y, w, h = bbox
            x1 = int(x - w / 2)
            y1 = int(y - h / 2)
            x2 = int(x + w / 2)
            y2 = int(y + h / 2)
            cls = self.class_names.index(label)
            
            if orig_width is not None and orig_height is not None:
                scale_x = orig_width / self.width
                scale_y = orig_height / self.height
                x1 = int(x1 * scale_x)
                y1 = int(y1 * scale_y)
                x2 = int(x2 * scale_x)
                y2 = int(y2 * scale_y)
            
            results.append((x1, y1, x2, y2, float(conf), cls))

        return results, image_resized

    def draw_boxes(self, frame, detections):
        """
                검출된 객체 bbox를 frame 위에 그려줌
        """
        for (x1, y1, x2, y2, conf, cls) in detections:
            label = f"{self.class_names[cls]} [{conf:.2f}]"
            color = self.class_colors[self.class_names[cls]]
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, color, 2)
        return frame

