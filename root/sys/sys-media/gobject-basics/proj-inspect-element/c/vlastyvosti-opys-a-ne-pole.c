static void
print_properties (GObjectClass * oclass)
{
  GParamSpec **props;
  guint n = 0, i;

  props = g_object_class_list_properties (oclass, &n);
  g_print ("\nВластивості (%u):\n", n);

  for (i = 0; i < n; i++) {
    GParamSpec *p = props[i];
    const gchar *blurb = g_param_spec_get_blurb (p);

    g_print ("\n  %s   ← оголошено в %s\n",
        g_param_spec_get_name (p), g_type_name (p->owner_type));
    if (blurb)
      g_print ("      %s\n", blurb);
    print_value_range (p);
    print_flags (p);
  }

  /* Наш тут лише МАСИВ. Самі описи належать класові й живуть,
     поки живе клас, — звільняти їх не можна.                    */
  g_free (props);
}
