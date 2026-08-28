void dtmf_init(dtmf_bank_t *b)
{
    for (int i = 0; i < N_TONES; ++i) {
        int k = (int)(0.5f + (float)N_BLOCK * dtmf_freq[i] / FS); // найближчий бін
        float w = 2.0f * (float)M_PI * k / N_BLOCK;
        b->g[i].coeff = 2.0f * cosf(w);
        b->g[i].s1 = b->g[i].s2 = 0.0f;
    }
    b->energy = 0.0f;
    b->n = 0;
}
