#include <algorithm>

struct Box { int x, y, w, h; float score; };

float iou(const Box &a, const Box &b) {
    int x1 = std::max(a.x, b.x);                    // ліва межа перетину
    int y1 = std::max(a.y, b.y);                    // верхня
    int x2 = std::min(a.x + a.w, b.x + b.w);        // права
    int y2 = std::min(a.y + a.h, b.y + b.h);        // нижня
    int iw = x2 - x1, ih = y2 - y1;
    if (iw <= 0 || ih <= 0) return 0.0f;            // не перетинаються
    float inter = static_cast<float>(iw) * ih;
    float uni   = static_cast<float>(a.w) * a.h + static_cast<float>(b.w) * b.h - inter;
    return inter / uni;
}
