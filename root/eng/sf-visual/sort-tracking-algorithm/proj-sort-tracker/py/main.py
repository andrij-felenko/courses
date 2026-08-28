import numpy as np
from scipy.optimize import linear_sum_assignment


def convert_bbox_to_z(bbox):
    """Перетворює [x1, y1, x2, y2] на вектор виміру [u, v, s, r]."""
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    u = bbox[0] + w / 2.0
    v = bbox[1] + h / 2.0
    s = w * h
    r = w / float(h) if h > 0 else 1.0
    return np.array([u, v, s, r]).reshape((4, 1))


def convert_x_to_bbox(x):
    """Перетворює стан Калмана [u, v, s, r, ...] на [x1, y1, x2, y2]."""
    u, v, s, r = x[0, 0], x[1, 0], x[2, 0], x[3, 0]
    if s <= 0 or r <= 0:
        return np.zeros(4)
    w = np.sqrt(s * r)
    h = np.sqrt(s / r)
    return np.array([u - w / 2.0, v - h / 2.0, u + w / 2.0, v + h / 2.0])


def compute_iou(bb_test, bb_gt):
    """Обчислює IoU між двома прямокутними рамками."""
    xx1 = np.maximum(bb_test[0], bb_gt[0])
    yy1 = np.maximum(bb_test[1], bb_gt[1])
    xx2 = np.minimum(bb_test[2], bb_gt[2])
    yy2 = np.minimum(bb_test[3], bb_gt[3])
    w = np.maximum(0.0, xx2 - xx1)
    h = np.maximum(0.0, yy2 - yy1)
    inter = w * h
    area_test = (bb_test[2] - bb_test[0]) * (bb_test[3] - bb_test[1])
    area_gt = (bb_gt[2] - bb_gt[0]) * (bb_gt[3] - bb_gt[1])
    union = area_test + area_gt - inter
    return inter / union if union > 0 else 0.0


class KalmanBoxTracker:
    count = 0

    def __init__(self, bbox):
        # 7D стан: [u, v, s, r, u_dot, v_dot, s_dot]
        self.x = np.zeros((7, 1))
        self.x[:4] = convert_bbox_to_z(bbox)
        
        # Матриця коваріації стану P
        self.P = np.diag([10.0, 10.0, 10.0, 10.0, 1000.0, 1000.0, 1000.0])
        
        # Матриця переходу F (dt = 1)
        self.F = np.eye(7)
        for i in range(3):
            self.F[i, i + 4] = 1.0
            
        # Матриця виміру H (4x7)
        self.H = np.zeros((4, 7))
        for i in range(4):
            self.H[i, i] = 1.0
            
        # Шуми Q та R
        self.Q = np.diag([1.0, 1.0, 1.0, 1.0, 10.0, 10.0, 10.0]) * 0.01
        self.R = np.diag([1.0, 1.0, 10.0, 10.0]) * 1.0
        
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.hits = 1
        self.hit_streak = 1
        self.age = 0

    def predict(self):
        # x = F * x
        self.x = np.dot(self.F, self.x)
        # P = F * P * F^T + Q
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        return convert_x_to_bbox(self.x)

    def update(self, bbox):
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        z = convert_bbox_to_z(bbox)
        
        # Інновація y = z - H * x
        y = z - np.dot(self.H, self.x)
        # S = H * P * H^T + R
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        # K = P * H^T * inv(S)
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        # x = x + K * y
        self.x = self.x + np.dot(K, y)
        # P = (I - K * H) * P
        I = np.eye(7)
        self.P = np.dot(I - np.dot(K, self.H), self.P)


class Sort:
    def __init__(self, max_age=1, min_hits=3, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0

    def update(self, detections=np.empty((0, 5))):
        """
        detections: np.array розмірності (N, 5), де кожен рядок це [x1, y1, x2, y2, score].
        Повертає масив активних треків [x1, y1, x2, y2, track_id].
        """
        self.frame_count += 1
        # 1. Передбачення для всіх наявних треків
        predicted_boxes = []
        to_del = []
        for i, trk in enumerate(self.trackers):
            box = trk.predict()
            if np.any(np.isnan(box)):
                to_del.append(i)
            else:
                predicted_boxes.append(box)
        for i in reversed(to_del):
            self.trackers.pop(i)

        # 2. Обчислення матриці IoU та зіставлення
        num_trks = len(self.trackers)
        num_dets = len(detections)
        matched, unmatched_dets, unmatched_trks = [], list(range(num_dets)), list(range(num_trks))

        if num_trks > 0 and num_dets > 0:
            iou_matrix = np.zeros((num_trks, num_dets))
            for t_idx, trk_box in enumerate(predicted_boxes):
                for d_idx, det in enumerate(detections):
                    iou_matrix[t_idx, d_idx] = compute_iou(trk_box, det[:4])

            # Розв'язання задачі призначення: мінімізація -IoU
            row_ind, col_ind = linear_sum_assignment(-iou_matrix)
            
            unmatched_trks = []
            unmatched_dets = []
            matched = []

            for r, c in zip(row_ind, col_ind):
                if iou_matrix[r, c] < self.iou_threshold:
                    unmatched_trks.append(r)
                    unmatched_dets.append(c)
                else:
                    matched.append((r, c))

            for t_idx in range(num_trks):
                if t_idx not in row_ind:
                    unmatched_trks.append(t_idx)
            for d_idx in range(num_dets):
                if d_idx not in col_ind:
                    unmatched_dets.append(d_idx)

        # 3. Оновлення зіставлених треків
        for t_idx, d_idx in matched:
            self.trackers[t_idx].update(detections[d_idx, :4])

        # 4. Створення нових треків для незіставлених детекцій
        for d_idx in unmatched_dets:
            new_trk = KalmanBoxTracker(detections[d_idx, :4])
            self.trackers.append(new_trk)

        # 5. Збір підтверджених результатів та видалення застарілих
        res = []
        i = len(self.trackers)
        for trk in reversed(self.trackers):
            d = convert_x_to_bbox(trk.x)
            if (trk.time_since_update < 1) and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                res.append(np.concatenate((d, [trk.id])).reshape(1, -1))
            i -= 1
            if trk.time_since_update > self.max_age:
                self.trackers.pop(i)

        if len(res) > 0:
            return np.vstack(res)
        return np.empty((0, 5))
