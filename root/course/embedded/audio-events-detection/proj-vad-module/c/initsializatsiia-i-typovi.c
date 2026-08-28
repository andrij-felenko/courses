void vad_init(vad_t *v, const vad_config_t *cfg)
{
    v->cfg    = *cfg;
    v->noise  = cfg->noise_init;      // початкова груба оцінка фону
    v->active = false;
    v->hang   = 0;
}

void vad_config_default(vad_config_t *cfg)
{
    cfg->frame_len   = 256;    // при 16 кГц це 16 мс — стандартне вікно
    cfg->k_up        = 64;     // Q4: 64/16 = 4.0 — увійти вчетверо над фоном
    cfg->k_down      = 32;     // Q4: 32/16 = 2.0 — вийти вдвічі над фоном
    cfg->alpha_shift = 7;      // фон += (e−фон) >> 7  — повільне, важке середнє
    cfg->hang_frames = 12;     // 12·16 мс ≈ 190 мс хвоста
    cfg->zcr_high    = 90;     // «висока ZCR» для кадру 256 (див. нижче)
    cfg->noise_init  = 40000;  // груба стартова оцінка суми квадратів у тиші
}
