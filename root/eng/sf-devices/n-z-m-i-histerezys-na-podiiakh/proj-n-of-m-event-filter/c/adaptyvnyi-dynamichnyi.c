/**
 * @brief Адаптивний розрахунок порогу на основі ковзної дисперсії шуму
 */
void event_filter_adaptive_adjust(event_filter_fast32_t *f, uint32_t short_term_glitches) {
    /* Якщо за останні 1000 відліків зафіксовано понад 50 шумових сплесків */
    if (short_term_glitches > 50U) {
        /* Збільшуємо жорсткість фільтра: N_on підіймаємо до 7, N_off опускаємо до 1 */
        f->n_on  = (f->m_window >= 8U) ? (f->m_window - 1U) : f->m_window;
        f->n_off = 1U;
        f->status_flags |= EVENT_FILTER_STATUS_HIGH_NOISE_WARN;
    } else {
        /* Повернення до стандартної чутливості 6 з 8 */
        f->n_on  = (f->m_window * 3U) / 4U;
        f->n_off = f->m_window / 4U;
        f->status_flags &= (uint8_t)~EVENT_FILTER_STATUS_HIGH_NOISE_WARN;
    }
}
