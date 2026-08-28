// Розширюємо профіль: чи дозволяти напругу-критерій під навантаженням.
// Під розрядом сира напруга змішує заряд із падінням I·R — для рівняння це шум.
static uint16_t cell_metric_loaded(const chem_cfg_t *c, const pack_state_t *p,
                                    int i, bool under_load)
{
    if (under_load)
        return p->soc[i];          // під навантаженням — ТІЛЬКИ за зарядом, байдуже хімія

    return cell_metric(c, p, i);   // у спокої / на заряді — як домовлялись (U чи SOC)
}
