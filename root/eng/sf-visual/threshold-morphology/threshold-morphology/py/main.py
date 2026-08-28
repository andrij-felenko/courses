# erode: out[y][x] = 255, лише якщо ВЕСЬ окіл 3×3 білий (інакше 0)
mn = 255
for dy in (-1, 0, 1):
    for dx in (-1, 0, 1):
        if mask[y+dy][x+dx] < mn:
            mn = mask[y+dy][x+dx]
ero[y][x] = mn

# dilate: out[y][x] = 255, якщо в околі 3×3 є хоч один білий
mx = 0
for dy in (-1, 0, 1):
    for dx in (-1, 0, 1):
        if ero[y+dy][x+dx] > mx:
            mx = ero[y+dy][x+dx]
out[y][x] = mx   # відкриття = erode, потім dilate
