static uint8_t dispL[H][W];   // диспаритет, порахований L→R (опора — лівий)
static uint8_t dispR[H][W];   // диспаритет, порахований R→L (опора — правий)

#define LR_TOL 1              // допуск розбіжності, пікселів

void left_right_check(void)
{
    for (int y = HALF; y < H - HALF; ++y) {
        for (int x = HALF + DMAX; x < W - HALF; ++x) {

            uint8_t d = dispL[y][x];
            if (d == INVALID_DISP) continue;

            // піксель праворуч, на який показує лівий збіг
            int xr = x - d;
            if (xr < HALF) { dispL[y][x] = INVALID_DISP; continue; }

            uint8_t d2 = dispR[y][xr];        // що каже зворотне зіставлення
            if (d2 == INVALID_DISP) { dispL[y][x] = INVALID_DISP; continue; }

            // згода в межах допуску — лишаємо; ні — викидаємо як оклюзію/помилку
            int diff = (int)d - (int)d2;
            if (diff < 0) diff = -diff;
            if (diff > LR_TOL)
                dispL[y][x] = INVALID_DISP;
        }
    }
}
