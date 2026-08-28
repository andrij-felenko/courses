static const gchar *
star (GType t)
{
  /* об'єктні, боксовані та рядкові типи їдуть у зворотний виклик покажчиком */
  return (G_TYPE_IS_CLASSED (t) || G_TYPE_IS_BOXED (t)
      || t == G_TYPE_STRING || t == G_TYPE_POINTER) ? " *" : " ";
}

static void
print_signals (GType type)
{
  g_print ("\nСигнали:\n");

  for (; type != 0; type = g_type_parent (type)) {
    guint *ids, n = 0, i, k;

    ids = g_signal_list_ids (type, &n);       /* масив наш → g_free */
    for (i = 0; i < n; i++) {
      GSignalQuery q;
      GString *sig;
      GType rt;

      g_signal_query (ids[i], &q);
      if (q.signal_id == 0)                   /* сигнал уже не існує */
        continue;

      /* У типах сигналу молодший біт може нести службовий прапорець
         G_SIGNAL_TYPE_STATIC_SCOPE — його треба зняти маскою.       */
      rt = q.return_type & ~G_SIGNAL_TYPE_STATIC_SCOPE;

      sig = g_string_new (NULL);
      g_string_append_printf (sig, "%s%suser_function (%s *self",
          g_type_name (rt), star (rt), g_type_name (q.itype));
      for (k = 0; k < q.n_params; k++) {
        GType pt = q.param_types[k] & ~G_SIGNAL_TYPE_STATIC_SCOPE;
        g_string_append_printf (sig, ", %s%sarg%u", g_type_name (pt), star (pt), k);
      }
      g_string_append (sig, ", gpointer user_data)");

      g_print ("  \"%s\"  ← від %s%s\n      %s\n", q.signal_name,
          g_type_name (q.itype),
          (q.signal_flags & G_SIGNAL_ACTION) ? "   [дія: не підписка, а виклик]" : "",
          sig->str);
      g_string_free (sig, TRUE);
    }
    g_free (ids);
  }
}
