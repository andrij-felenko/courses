typedef struct { float x1, y1, x2, y2, score; int cls; } det_t;

// сортування за спаданням упевненості (проста бульбашка — масивів тут небагато)
static void sort_by_score(det_t *d, int n) {
    for (int i = 0; i < n - 1; i++)
        for (int j = 0; j < n - 1 - i; j++)
            if (d[j].score < d[j + 1].score) {
                det_t tmp = d[j]; d[j] = d[j + 1]; d[j + 1] = tmp;
            }
}

static float iou_det(det_t a, det_t b) {
    float ix1 = a.x1 > b.x1 ? a.x1 : b.x1, iy1 = a.y1 > b.y1 ? a.y1 : b.y1;
    float ix2 = a.x2 < b.x2 ? a.x2 : b.x2, iy2 = a.y2 < b.y2 ? a.y2 : b.y2;
    float iw = ix2 - ix1, ih = iy2 - iy1;
    if (iw <= 0 || ih <= 0) return 0.0f;
    float inter = iw * ih;
    float uni = (a.x2-a.x1)*(a.y2-a.y1) + (b.x2-b.x1)*(b.y2-b.y1) - inter;
    return inter / uni;
}

// NMS на місці: лишені рамки позначаємо keep[i]=1. Повертає кількість лишених.
int nms(det_t *d, int n, float iou_thr, int *keep) {
    sort_by_score(d, n);
    for (int i = 0; i < n; i++) keep[i] = 1;
    int kept = 0;
    for (int i = 0; i < n; i++) {
        if (!keep[i]) continue;          // вже придушена сильнішою
        kept++;
        for (int j = i + 1; j < n; j++) {
            if (!keep[j]) continue;
            if (d[j].cls != d[i].cls) continue;          // різні класи не конкурують
            if (iou_det(d[i], d[j]) > iou_thr) keep[j] = 0;  // двійник — геть
        }
    }
    return kept;
}
