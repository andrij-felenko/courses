// рамка: x1,y1 — лівий верх; x2,y2 — правий низ
typedef struct { float x1, y1, x2, y2; } box_t;

static float area(box_t b) {
    return (b.x2 - b.x1) * (b.y2 - b.y1);
}

float iou(box_t a, box_t b) {
    // перетин: правіший лівий край ... лівіший правий край
    float ix1 = a.x1 > b.x1 ? a.x1 : b.x1;   // max(x1)
    float iy1 = a.y1 > b.y1 ? a.y1 : b.y1;   // max(y1)
    float ix2 = a.x2 < b.x2 ? a.x2 : b.x2;   // min(x2)
    float iy2 = a.y2 < b.y2 ? a.y2 : b.y2;   // min(y2)

    float iw = ix2 - ix1;                      // ширина перетину
    float ih = iy2 - iy1;                      // висота перетину
    if (iw <= 0.0f || ih <= 0.0f) return 0.0f; // не торкаються
    float inter = iw * ih;

    float uni = area(a) + area(b) - inter;     // об'єднання без подвійного рахунку
    return inter / uni;
}
