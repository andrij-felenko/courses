// Розмітка одного об'єкта: клас + рамка у частках кадру [0..1]
typedef struct {
    int   cls;        // номер класу: 0 = людина, 1 = машина, ...
    float cx, cy;     // центр рамки, частка ширини/висоти
    float w,  h;      // ширина й висота рамки, частка кадру
} Label;

// Перевести рамку в пікселях у нормований запис
Label box_to_label(int cls, int x0, int y0, int x1, int y1,
                   int img_w, int img_h) {
    Label L;
    L.cls = cls;
    L.cx  = (float)(x0 + x1) / 2 / img_w;   // центр X у частках
    L.cy  = (float)(y0 + y1) / 2 / img_h;   // центр Y у частках
    L.w   = (float)(x1 - x0)     / img_w;   // ширина у частках
    L.h   = (float)(y1 - y0)     / img_h;   // висота у частках
    return L;
}
