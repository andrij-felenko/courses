typedef struct {
    int current;        // поточна сходинка
    int up_confirm;     // лічильник «легко влазить» поспіль (для росту)
} abr_player_t;

int abr_player_step(abr_player_t *p, uint32_t seg_bytes, uint32_t dl_ms)
{
    int want = abr_pick_rendition(seg_bytes, dl_ms);

    if (want < p->current) {
        // вниз — БЕЗ роздумів: порожній буфер найгірший
        p->current   = want;
        p->up_confirm = 0;
    } else if (want > p->current) {
        // вгору — лише після трьох підтверджень поспіль
        if (++p->up_confirm >= 3) {
            p->current   += 1;          // піднімаємось на ОДНУ сходинку
            p->up_confirm = 0;
        }
    } else {
        p->up_confirm = 0;              // тупцюємо — скидаємо лічильник
    }
    return p->current;
}
