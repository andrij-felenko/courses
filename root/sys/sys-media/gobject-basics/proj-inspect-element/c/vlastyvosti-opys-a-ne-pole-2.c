static void
print_value_range (GParamSpec * p)
{
  GValue def = G_VALUE_INIT;
  gchar *ds;

  /* Універсальний спосіб надрукувати типове значення будь-чого:
     завести GValue правильного типу, попросити опис покласти туди
     своє типове й перетворити на текст.                          */
  g_value_init (&def, p->value_type);
  g_param_value_set_default (p, &def);
  ds = g_strdup_value_contents (&def);

  if (G_IS_PARAM_SPEC_UINT (p)) {
    GParamSpecUInt *s = G_PARAM_SPEC_UINT (p);
    g_print ("      ціле без знака, межі %u … %u, типово %s\n",
        s->minimum, s->maximum, ds);
  } else if (G_IS_PARAM_SPEC_INT (p)) {
    GParamSpecInt *s = G_PARAM_SPEC_INT (p);
    g_print ("      ціле зі знаком, межі %d … %d, типово %s\n",
        s->minimum, s->maximum, ds);
  } else if (G_IS_PARAM_SPEC_INT64 (p)) {
    GParamSpecInt64 *s = G_PARAM_SPEC_INT64 (p);
    g_print ("      ціле 64 біти, межі %" G_GINT64_FORMAT
        " … %" G_GINT64_FORMAT ", типово %s\n", s->minimum, s->maximum, ds);
  } else if (G_IS_PARAM_SPEC_UINT64 (p)) {
    GParamSpecUInt64 *s = G_PARAM_SPEC_UINT64 (p);
    g_print ("      ціле 64 біти без знака, межі %" G_GUINT64_FORMAT
        " … %" G_GUINT64_FORMAT ", типово %s\n", s->minimum, s->maximum, ds);
  } else if (G_IS_PARAM_SPEC_DOUBLE (p)) {
    GParamSpecDouble *s = G_PARAM_SPEC_DOUBLE (p);
    g_print ("      дробове, межі %g … %g, типово %s\n",
        s->minimum, s->maximum, ds);
  } else if (G_IS_PARAM_SPEC_BOOLEAN (p)) {
    g_print ("      логічне, типово %s\n", ds);
  } else if (G_IS_PARAM_SPEC_STRING (p)) {
    g_print ("      рядок, типово %s\n", ds);
  } else if (G_IS_PARAM_SPEC_ENUM (p)) {
    GEnumClass *ec = G_PARAM_SPEC_ENUM (p)->enum_class;
    guint k;
    g_print ("      перелік %s, типово %s\n", g_type_name (p->value_type), ds);
    for (k = 0; k < ec->n_values; k++)
      g_print ("          (%d) %-14s %s\n", ec->values[k].value,
          ec->values[k].value_nick, ec->values[k].value_name);
  } else if (G_IS_PARAM_SPEC_FLAGS (p)) {
    GFlagsClass *fc = G_PARAM_SPEC_FLAGS (p)->flags_class;
    guint k;
    g_print ("      набір прапорців %s, типово %s\n",
        g_type_name (p->value_type), ds);
    for (k = 0; k < fc->n_values; k++)
      g_print ("          (0x%08x) %-14s %s\n", fc->values[k].value,
          fc->values[k].value_nick, fc->values[k].value_name);
  } else {
    g_print ("      %s, типово %s\n", g_type_name (p->value_type), ds);
  }

  g_free (ds);
  g_value_unset (&def);     /* для рядків і об'єктів це справжнє звільнення */
}
