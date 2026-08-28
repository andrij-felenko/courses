// по одному примітиву за виклик: 10 000 прямокутників = 10 000 віртуальних викликів
struct PaintEngine {
    virtual void drawRect(const Rect& r) = 0;
    virtual ~PaintEngine() = default;
};

// як у Qt: партія за виклик — один віртуальний виклик на весь масив
struct PaintEngine {
    virtual void drawRects(const Rect* rects, int count) = 0;
    virtual ~PaintEngine() = default;
};
