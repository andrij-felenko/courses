typedef enum { CHG_IDLE, CHG_PRECHARGE, CHG_FAST, CHG_DONE } bq_phase_t;

typedef struct {
    bq_phase_t phase;      /* фаза заряду з CHRG_STAT */
    uint8_t    vbus_type;  /* 0 нема/невідомо, 1 USB-хост, 2 адаптер, 3 OTG */
    bool       power_good; /* вхід придатний */
    bool       in_dpm;     /* активний ВХІДНИЙ контур (VINDPM або IINDPM) */
    bool       in_thermal; /* активне теплове регулювання (гарячий кристал) */
    bool       in_vsysmin; /* комірка нижча за VSYSMIN */
} bq_status_t;

int bq_read_status(bq_status_t *s)
{
    uint8_t r;
    int rc = bq_i2c_read(BQ_REG08, &r);
    if (rc) return rc;
    s->vbus_type  = (r >> 6) & 0x03;
    s->phase      = (bq_phase_t)((r >> 4) & 0x03);
    s->in_dpm     = (r >> 3) & 1;
    s->power_good = (r >> 2) & 1;
    s->in_thermal = (r >> 1) & 1;
    s->in_vsysmin = (r >> 0) & 1;
    return 0;
}
