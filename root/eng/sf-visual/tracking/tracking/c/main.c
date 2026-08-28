typedef struct { float x, y, w, h; } Rect;   // центр (x,y) і розмір

// перекриття двох рамок: перетин до об'єднання (0..1)
static float iou(Rect a, Rect b) {
    float ax0 = a.x - a.w/2, ax1 = a.x + a.w/2;   // ліва/права a
    float ay0 = a.y - a.h/2, ay1 = a.y + a.h/2;   // верх/низ a
    float bx0 = b.x - b.w/2, bx1 = b.x + b.w/2;
    float by0 = b.y - b.h/2, by1 = b.y + b.h/2;

    float ix = fmaxf(0.0f, fminf(ax1,bx1) - fmaxf(ax0,bx0));  // ширина перетину
    float iy = fmaxf(0.0f, fminf(ay1,by1) - fmaxf(ay0,by0));  // висота перетину
    float inter = ix * iy;
    float uni   = a.w*a.h + b.w*b.h - inter;       // об'єднання = сума − перетин
    return uni > 0.0f ? inter / uni : 0.0f;
}

// прийняти детекцію det у трек, якщо вона добре лягає на прогноз
bool associate(Rect prev, float vx, float vy, Rect det, float dt) {
    Rect pred = prev;
    pred.x += vx * dt;          // прогноз: положення + швидкість × Δt
    pred.y += vy * dt;
    return iou(pred, det) >= 0.3f;   // поріг перекриття — типово 0.3
}
