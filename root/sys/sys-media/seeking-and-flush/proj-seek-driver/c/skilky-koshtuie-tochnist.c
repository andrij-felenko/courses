/* Скільки коштує точність. Обидва режими міряємо однаково: спершу відходимо
   на початок, щоб кожен вимір починався з тієї самої відстані, і аж потім
   стрибаємо в ціль. Перший прохід розігрівальний — він гріє кеш сторінок
   файлу, і без нього перший режим завжди «повільніший» просто тому, що перший. */
static void
compare_accuracy (Player *p, gint64 target)
{
  static const struct { const char *name; GstSeekFlags flags; } modes[] = {
    { "KEY_UNIT", GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_KEY_UNIT },
    { "ACCURATE", GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_ACCURATE },
  };
  guint pass, i;

  for (pass = 0; pass < 2; pass++) {
    if (pass)
      g_print ("ціль %" GST_TIME_FORMAT "\n", GST_TIME_ARGS (target));

    for (i = 0; i < G_N_ELEMENTS (modes); i++) {
      gint64 spent, got;
      SeekResult r;

      seek_and_wait (p, 0, GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_KEY_UNIT, &spent);
      r = seek_and_wait (p, target, modes[i].flags, &spent);
      if (!pass)
        continue;

      if (r != SEEK_OK) {
        g_print ("  %-8s → %s\n", modes[i].name, seek_result_name (r));
        continue;
      }
      got = position_now (p);
      g_print ("  %-8s  %7.1f мс   влучили в %" GST_TIME_FORMAT
               "   промах %+.3f с\n",
               modes[i].name, spent / 1000.0, GST_TIME_ARGS (got),
               (double) (got - target) / GST_SECOND);
    }
  }
}
