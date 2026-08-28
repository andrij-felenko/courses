// erode: out[y][x] = 255, лише якщо ВЕСЬ окіл 3×3 білий (інакше 0)
uint8_t mn = 255;
for (int dy = -1; dy <= 1; ++dy)
    for (int dx = -1; dx <= 1; ++dx)
        if (mask[y+dy][x+dx] < mn) mn = mask[y+dy][x+dx];
ero[y][x] = mn;

// dilate: out[y][x] = 255, якщо в околі 3×3 є хоч один білий
uint8_t mx = 0;
for (int dy = -1; dy <= 1; ++dy)
    for (int dx = -1; dx <= 1; ++dx)
        if (ero[y+dy][x+dx] > mx) mx = ero[y+dy][x+dx];
out[y][x] = mx;   // відкриття = erode, потім dilate
