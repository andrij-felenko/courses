auto columnOf = [&](double x) -> int {
    return static_cast<int>((x - minX) / range * pixelWidth);
};

for (qsizetype i = 0; i < sliceCount; ++i) {
    const QPointF &p = *(sliceBegin + i);
    const int col = std::clamp(columnOf(p.x()), 0, pixelWidth - 1);
    if (col != curCol) {
        flush();                    // віддати першу, мін, макс, останню попередньої колонки
        curCol   = col;
        firstIdx = i;
        minIdx   = i;
        maxIdx   = i;
    } else {
        if (p.y() < (sliceBegin + minIdx)->y()) minIdx = i;
        if (p.y() > (sliceBegin + maxIdx)->y()) maxIdx = i;
    }
    lastIdx = i;
}
flush();
