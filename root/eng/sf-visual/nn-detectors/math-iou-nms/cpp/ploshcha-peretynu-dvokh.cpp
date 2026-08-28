float iou(box_t a, box_t b) {
    float ix1 = fmaxf(a.x1, b.x1), iy1 = fmaxf(a.y1, b.y1);
    float ix2 = fminf(a.x2, b.x2), iy2 = fminf(a.y2, b.y2);
    float iw = ix2 - ix1, ih = iy2 - iy1;
    if (iw <= 0.0f || ih <= 0.0f) return 0.0f;     // не торкаються — перетин 0
    float inter = iw * ih;
    float areaA = (a.x2 - a.x1) * (a.y2 - a.y1);
    float areaB = (b.x2 - b.x1) * (b.y2 - b.y1);
    return inter / (areaA + areaB - inter);         // ∩ / ∪
}
