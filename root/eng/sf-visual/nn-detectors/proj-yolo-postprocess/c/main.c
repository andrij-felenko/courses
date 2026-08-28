// out — сирий тензор від NPU [S*S*K]; final[] — куди скласти лишені рамки.
// Повертає кількість знайдених об'єктів.
int yolo_postprocess(const float *out, float conf_thr, float iou_thr,
                     det_t *final, int final_cap) {
    static det_t dets[MAX_DET];
    static int   keep[MAX_DET];

    int n = collect(out, conf_thr, dets);             // декодувати + відсіяти слабкі
    nms(dets, n, iou_thr, keep);                      // прибрати двійників

    int m = 0;
    for (int i = 0; i < n && m < final_cap; i++)
        if (keep[i]) final[m++] = dets[i];            // зібрати лишені
    return m;
}

// приклад виклику:
//   det_t found[64];
//   int k = yolo_postprocess(npu_output, 0.30f, 0.45f, found, 64);
//   for (int i = 0; i < k; i++)
//       printf("cls=%d score=%.2f  [%.0f %.0f %.0f %.0f]\n",
//              found[i].cls, found[i].score,
//              found[i].x1, found[i].y1, found[i].x2, found[i].y2);
