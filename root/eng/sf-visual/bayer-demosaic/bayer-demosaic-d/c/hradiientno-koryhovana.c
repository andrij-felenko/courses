#include <stdint.h>
#include <stdlib.h>   // abs

// Внутрішній червоний піксель (y,x парні). raw — сира RGGB-мозаїка.
// Повертає оцінку зеленого, зважену вздовж напрямку з меншим перепадом.
static uint8_t green_at_red(int H, int W, const uint8_t raw[H][W], int y, int x) {
    int gl = raw[y][x-1], gr = raw[y][x+1];   // зелені ліворуч / праворуч
    int gu = raw[y-1][x], gd = raw[y+1][x];   // зелені зверху / знизу

    int dH = abs(gl - gr);                     // перепад по горизонталі
    int dV = abs(gu - gd);                     // перепад по вертикалі

    int wH = 1 + dV;        // вага горизонталі БІЛЬША, коли вертикальний перепад великий
    int wV = 1 + dH;        // (тобто межа вертикальна → інтерполюємо вздовж неї, по горизонталі)

    int hAvg = (gl + gr + 1) / 2;              // середнє вздовж горизонталі
    int vAvg = (gu + gd + 1) / 2;              // середнє вздовж вертикалі

    int g = (wH * hAvg + wV * vAvg + (wH + wV) / 2) / (wH + wV);
    return (uint8_t)g;
}
