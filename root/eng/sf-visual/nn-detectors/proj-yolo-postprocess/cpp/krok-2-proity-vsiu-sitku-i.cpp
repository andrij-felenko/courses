// повертає кількість рамок, записаних у dets[]; не більше MAX_DET
static int collect(const float *out, float conf_thr, det_t *dets) {
    int n = 0;
    for (int cy = 0; cy < S; cy++)
        for (int cx = 0; cx < S; cx++)
            for (int a = 0; a < B; a++) {
                det_t d = decode(out, cx, cy, a);
                if (d.score < conf_thr) continue;     // слабка — геть одразу
                if (n < MAX_DET) dets[n++] = d;       // стеля — захист від переповнення
            }
    return n;
}
