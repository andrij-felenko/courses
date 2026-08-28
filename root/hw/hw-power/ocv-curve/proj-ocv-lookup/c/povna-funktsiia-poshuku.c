typedef struct {
    uint16_t soc_pm;     // заряд, проміле
    uint16_t sigma_pm;   // ПОХИБКА цієї ж відповіді, проміле
    bool     usable;     // чи взагалі варто цю відповідь кудись подіти
} ocv_read_t;

#define SIGMA_V_01MV   50u    // похибка вольтметра: 5 мВ у одиницях 0.1 мВ
#define SIGMA_MAX_PM  150u    // стеля довіри: понад 15 % — відповідь у смітник

ocv_read_t ocv_to_soc(const ocv_table_t *t, uint16_t v_01mv) {
    ocv_read_t r;

    // Поза таблицею відповіді немає: там крива не мірялася, і вигадувати її
    // екстраполяцією — те саме, що вигадувати цифри.
    if (v_01mv < t->k[0].v_01mv) {
        r.soc_pm = t->k[0].soc_pm;
        r.sigma_pm = SIGMA_MAX_PM; r.usable = false; return r;
    }
    if (v_01mv > t->k[t->n - 1].v_01mv) {
        r.soc_pm = t->k[t->n - 1].soc_pm;
        r.sigma_pm = SIGMA_MAX_PM; r.usable = false; return r;
    }

    uint8_t  i    = find_segment(t, v_01mv);
    uint32_t dv   = (uint32_t)(t->k[i+1].v_01mv - t->k[i].v_01mv);   // > 0: гарантія генератора
    uint32_t dsoc = (uint32_t)(t->k[i+1].soc_pm - t->k[i].soc_pm);
    uint32_t off  = (uint32_t)(v_01mv - t->k[i].v_01mv);

    // Лінійна інтерполяція з округленням до найближчого (+dv/2 перед діленням)
    r.soc_pm = (uint16_t)(t->k[i].soc_pm + (off * dsoc + dv / 2) / dv);

    // Похибка з нахилу ТОГО САМОГО відрізка: σ_SoC = σ_V · ΔSoC / ΔV
    r.sigma_pm = (uint16_t)((SIGMA_V_01MV * dsoc + dv / 2) / dv);
    if (r.sigma_pm == 0) r.sigma_pm = 1;        // нуль зіпсує ділення при злитті
    r.usable = (r.sigma_pm <= SIGMA_MAX_PM);
    return r;
}
