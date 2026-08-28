// Дебаунс рівня CC: рівень визнаємо стабільним лише після M однакових поспіль.
#define CC_STABLE_N 5

static cc_level_t stable_level = CC_NONE;
static cc_level_t cand = CC_NONE;
static uint8_t    cand_cnt = 0;

cc_level_t cc_update(int mv) {
    cc_level_t lvl = cc_decode(mv, stable_level);   // спершу гістерезис
    if (lvl == cand) {
        if (cand_cnt < CC_STABLE_N) cand_cnt++;
        if (cand_cnt >= CC_STABLE_N) stable_level = lvl;  // визнали сталим
    } else {
        cand = lvl;            // рівень змінився — починаємо рахувати наново
        cand_cnt = 1;
    }
    return stable_level;
}
