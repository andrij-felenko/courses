int nms(det_t *d, int n, float tau, int *keep) {
    sort_desc_by_score(d, n);                 // крок 2
    for (int i = 0; i < n; i++) keep[i] = 1;
    for (int i = 0; i < n; i++) {
        if (!keep[i]) continue;               // вже придушена — пропустити
        for (int j = i + 1; j < n; j++) {     // лише дальші (вони слабші)
            if (!keep[j] || d[j].cls != d[i].cls) continue;
            if (iou(d[i].box, d[j].box) > tau) keep[j] = 0;   // крок 4
        }
    }
    int kept = 0; for (int i = 0; i < n; i++) kept += keep[i];
    return kept;
}
