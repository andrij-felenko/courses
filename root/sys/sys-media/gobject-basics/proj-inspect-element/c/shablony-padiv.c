static void
print_pad_templates (GstElementClass * eclass)
{
  GList *l;

  g_print ("\nШаблони падів:\n");
  for (l = gst_element_class_get_pad_template_list (eclass); l; l = l->next) {
    GstPadTemplate *t = GST_PAD_TEMPLATE (l->data);
    GstCaps *caps = gst_pad_template_get_caps (t);   /* нове посилання */
    gchar *s = gst_caps_to_string (caps);

    g_print ("  %-14s %s, %s\n      %s\n", t->name_template,
        t->direction == GST_PAD_SRC ? "вихід" : "вхід",
        t->presence == GST_PAD_ALWAYS ? "завжди" :
        t->presence == GST_PAD_SOMETIMES ? "інколи" : "на запит",
        s);

    g_free (s);
    gst_caps_unref (caps);      /* НЕ gst_object_unref: caps — міні-об'єкт */
  }
}
