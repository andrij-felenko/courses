// ЛЕГКИЙ слід у гарячому шляху: лише інкремент у RAM (наносекунди, без друку).
static volatile uint32_t g_trace[SUS_COUNT];

static inline void trace_hit(suspect_t s) { g_trace[s]++; }   // клич у гонці — дешево

// Важкий друк — ПІСЛЯ досліду, поза чутливим до часу вікном.
static void trace_dump_after_run(void) {
    for (int i = 0; i < SUS_COUNT; i++)
        JOURNAL_NOTE_FMT("вузол %-18s: спрацювань %lu\n", SUS_NAME[i],
                         (unsigned long)g_trace[i]);
}
