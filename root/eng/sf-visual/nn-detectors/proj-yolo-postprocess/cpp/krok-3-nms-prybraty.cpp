static float iou(det_t a, det_t b) {
    float ix1 = fmaxf(a.x1, b.x1), iy1 = fmaxf(a.y1, b.y1);
    float ix2 = fminf(a.x2, b.x2), iy2 = fminf(a.y2, b.y2);
    float iw = ix2 - ix1, ih = iy2 - iy1;
    if (iw <= 0.0f || ih <= 0.0f) return 0.0f;        // не торкаються
    float inter = iw * ih;
    float uni = (a.x2-a.x1)*(a.y2-a.y1) + (b.x2-b.x1)*(b.y2-b.y1) - inter;
    return inter / uni;
}

// NMS на місці: лишені позначає keep[i]=1; повертає їх кількість.
static int nms(det_t *d, int n, float iou_thr, int *keep) {
    // сортування за спаданням оцінки (n мала після фільтра — бульбашки досить)
    for (int i = 0; i < n - 1; i++)
        for (int j = 0; j < n - 1 - i; j++)
            if (d[j].score < d[j+1].score) {
                det_t tmp = d[j]; d[j] = d[j+1]; d[j+1] = tmp;
            }
    for (int i = 0; i < n; i++) keep[i] = 1;
    for (int i = 0; i < n; i++) {
        if (!keep[i]) continue;                       // вже придушена
        for (int j = i + 1; j < n; j++) {             // лише слабші за i
            if (!keep[j] || d[j].cls != d[i].cls) continue;   // різні класи не конкурують
            if (iou(d[i], d[j]) > iou_thr) keep[j] = 0;       // двійник — геть
        }
    }
    int kept = 0; for (int i = 0; i < n; i++) kept += keep[i];
    return kept;
}
