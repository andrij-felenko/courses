static void
print_flags (GParamSpec * p)
{
  GString *s = g_string_new (NULL);
  guint f = p->flags;

  if (f & G_PARAM_READABLE)       g_string_append (s, "читання, ");
  if (f & G_PARAM_WRITABLE)       g_string_append (s, "запис, ");
  if (f & G_PARAM_CONSTRUCT_ONLY) g_string_append (s, "лише при створенні, ");
  if (f & G_PARAM_DEPRECATED)     g_string_append (s, "застаріла, ");

  /* Біти GStreamer. Порядок важливий: PLAYING містить у собі PAUSED,
     PAUSED — READY, тож перемагає найвищий із виставлених.          */
  if (f & GST_PARAM_MUTABLE_PLAYING)
    g_string_append (s, "міняти можна аж до PLAYING, ");
  else if (f & GST_PARAM_MUTABLE_PAUSED)
    g_string_append (s, "міняти можна до PAUSED, ");
  else if (f & GST_PARAM_MUTABLE_READY)
    g_string_append (s, "міняти можна до READY, ");
  else if (f & G_PARAM_WRITABLE)
    g_string_append (s, "коли міняти — не позначено (покладайся на NULL), ");

  if (f & GST_PARAM_CONTROLLABLE)
    g_string_append (s, "можна вести кривою в часі, ");
  if (f & GST_PARAM_CONDITIONALLY_AVAILABLE)
    g_string_append (s, "є не в кожній збірці, ");

  if (s->len >= 2)
    g_string_truncate (s, s->len - 2);
  g_print ("      прапорці: %s\n", s->str);
  g_string_free (s, TRUE);
}
