// Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
int16_t xmin=32767, xmax=-32768, ymin=32767, ymax=-32768;

void calib_update(int16_t x, int16_t y) {   // виклик у циклі під час обертання
    if (x < xmin) xmin = x;  if (x > xmax) xmax = x;
    if (y < ymin) ymin = y;  if (y > ymax) ymax = y;
}

float heading_calibrated(int16_t x, int16_t y, float declination_deg) {
    int16_t xoff = (xmax + xmin) / 2;   // центр кола по X = зсув твердого заліза
    int16_t yoff = (ymax + ymin) / 2;
    return compass_heading(x - xoff, y - yoff, declination_deg);
}
