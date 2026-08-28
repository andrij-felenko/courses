static void
print_ancestry (GType type)
{
  GType chain[32];
  GType *ifaces;
  guint n_ifaces = 0;
  gint n = 0, i;

  for (; type != 0 && n < (gint) G_N_ELEMENTS (chain); type = g_type_parent (type))
    chain[n++] = type;
  if (n == 0)
    return;

  g_print ("\nРодовід:\n");
  for (i = n - 1; i >= 0; i--)
    g_print ("%*s%s\n", (n - 1 - i) * 2 + 2, "", g_type_name (chain[i]));

  ifaces = g_type_interfaces (chain[0], &n_ifaces);   /* масив наш */
  if (n_ifaces) {
    g_print ("  інтерфейси:");
    for (i = 0; i < (gint) n_ifaces; i++)
      g_print (" %s", g_type_name (ifaces[i]));
    g_print ("\n");
  }
  g_free (ifaces);
}
