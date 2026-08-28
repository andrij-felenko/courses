typedef enum { USE_RECORD, USE_FPV, USE_VISION } stream_role_t;

typedef struct {
    int   codec;          /* 0 = MJPEG/intra, 1 = H.264 */
    int   gop_len;        /* кадрів між I; 1 = кожен кадр I */
    int   use_b_frames;   /* B-кадри увімкнено? */
    int   intra_refresh;  /* смуга-оновлення замість цілих I */
} enc_config_t;

enc_config_t configure_encoder(stream_role_t role)
{
    enc_config_t c = {0};
    switch (role) {
    case USE_RECORD:                 /* запис на картку: лаг байдужий */
        c.codec = 1;  c.gop_len = 60; /* довгий GOP → максимум стиску */
        c.use_b_frames = 1;  c.intra_refresh = 0;
        break;
    case USE_FPV:                    /* пілот керує наживо: лаг головний */
        c.codec = 1;  c.gop_len = 10; /* короткий GOP → стійкість */
        c.use_b_frames = 0;           /* без B → без буфера реордера */
        c.intra_refresh = 1;          /* рівний бітрейт, короткі плями */
        break;
    case USE_VISION:                 /* детектор на борту: чисті кадри */
        c.codec = 0;  c.gop_len = 1;  /* intra-only: кожен кадр самостійний */
        c.use_b_frames = 0;  c.intra_refresh = 0;
        break;
    }
    return c;
}
