// Лічильник зубів від індуктивного давача обертів.
// На кожен зуб котушка дає сплеск ЕРС; компаратор перетворює його на фронт,
// що смикає переривання. Лічимо фронти за вікно часу → оберти.
volatile uint32_t teeth = 0;          // лічильник зубів (росте в перериванні)

void tooth_isr(void) { teeth++; }     // викликається фронтом від компаратора

float rpm(uint32_t teeth_count, uint32_t teeth_per_rev, float window_s) {
    float revs = (float)teeth_count / teeth_per_rev;   // скільки обертів за вікно
    return revs / window_s * 60.0f;                    // → обертів за хвилину
}
