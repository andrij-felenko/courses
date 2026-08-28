/* Дописати рядок у журнал. Викликається з потоків даних — отже, під замком. */
static void
journal (App *app, const gchar *fmt, ...)
{
  va_list ap;
  gchar *line;

  va_start (ap, fmt);
  line = g_strdup_vprintf (fmt, ap);
  va_end (ap);

  g_mutex_lock (&app->lock);
  g_string_append (app->journal, line);
  g_string_append_c (app->journal, '\n');
  g_mutex_unlock (&app->lock);

  g_free (line);
}

static const gchar *
veto_reason (App *app, GstElementFactory *factory)
{
  const gchar *name = gst_plugin_feature_get_name (GST_PLUGIN_FEATURE (factory));

  if (app->no_hw &&
      gst_element_factory_list_is_type (factory, GST_ELEMENT_FACTORY_TYPE_HARDWARE))
    return "апаратний (--no-hw)";

  for (gchar **p = app->veto; p && *p; p++)
    if (g_str_has_prefix (name, *p))
      return "у списку --skip";

  return NULL;
}

static GstAutoplugSelectResult
on_autoplug_select (GstElement *bin, GstPad *pad, GstCaps *caps,
                    GstElementFactory *factory, gpointer data)
{
  App *app = data;
  /* Усе нижче позичене в decodebin на час виклику: ні caps, ні factory
     ми не звільняємо. Треба пережити колбек — робіть власну копію
     (gst_caps_ref / g_strdup), інакше вказівник помре разом із кроком. */
  const gchar *name  = gst_plugin_feature_get_name (GST_PLUGIN_FEATURE (factory));
  const gchar *klass = gst_element_factory_get_metadata (factory,
                                                         GST_ELEMENT_METADATA_KLASS);
  guint rank = gst_plugin_feature_get_rank (GST_PLUGIN_FEATURE (factory));
  const gchar *media = gst_structure_get_name (gst_caps_get_structure (caps, 0));
  const gchar *why = veto_reason (app, factory);

  journal (app, "%-22s %-14s ранг %-5u %-30s %s%s", media, name, rank, klass,
           why ? "ПРОПУСК — " : "спроба", why ? why : "");

  if (why) {
    g_atomic_int_inc (&app->n_skip);
    return GST_AUTOPLUG_SELECT_SKIP;
  }
  g_atomic_int_inc (&app->n_try);
  return GST_AUTOPLUG_SELECT_TRY;
}
