// ── Журнал дослідів. Живе в прошивці НАЗАВЖДИ, але важить щось лише коли
//    зібрано з -DDEBUG_JOURNAL. Без прапорця макроси розкриваються в порожнечу.
#ifdef DEBUG_JOURNAL

  // Куди писати слід. journal_out — легкий вивід (напр. слід через зонд,
  // а не важкий друк у порт: чому саме легкий — див. пастку про гейзенбаг).
  #define JOURNAL(step, hypo, mask, active, verdict) \
      journal_out("#%d | гіпотеза: %s | маска=0x%08lX | активних=%d | -> %s\n", \
                  (step), (hypo), (unsigned long)(mask), (active), \
                  (verdict) ? "ВІДТВОРИВСЯ" : "чисто")

  #define JOURNAL_NOTE(msg)         journal_out("   %s\n", (msg))
  #define JOURNAL_NOTE_FMT(...)     journal_out(__VA_ARGS__)   // форматований рядок сліду

#else
  // Реліз: журналу нема зовсім. Аргументи-вирази навіть не обчислюються.
  #define JOURNAL(step, hypo, mask, active, verdict)  ((void)0)
  #define JOURNAL_NOTE(msg)                            ((void)0)
  #define JOURNAL_NOTE_FMT(...)                        ((void)0)
#endif

// Порахувати ввімкнені вузли в масці (для запису «скільки активних»).
static int popcount_mask(uint32_t m) {
    int c = 0;
    while (m) { c += (int)(m & 1u); m >>= 1; }
    return c;
}
