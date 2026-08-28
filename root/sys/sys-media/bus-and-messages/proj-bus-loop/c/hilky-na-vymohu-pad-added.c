/* Будує ланцюжок елементів, лінкує його й підтягує стан під конвеєр.
   Повертає вхідний pad першого елемента — його звільняє викликач. */
static GstPad *add_branch (App *app, const gchar *const *factories)
{
  GstElement *chain[4] = { NULL, NULL, NULL, NULL };
  guint n = 0;

  for (; n < G_N_ELEMENTS (chain) && factories[n] != NULL; n++) {
    chain[n] = gst_element_factory_make (factories[n], NULL);
    if (!chain[n]) {
      g_printerr ("бракує елемента «%s» — не встановлено плагін\n", factories[n]);
      return NULL;
    }
    gst_bin_add (GST_BIN (app->pipeline), chain[n]);   /* конвеєр забрав посилання */
    if (n > 0 && !gst_element_link (chain[n - 1], chain[n])) {
      g_printerr ("не з'єдналися %s і %s\n", factories[n - 1], factories[n]);
      return NULL;
    }
  }

  /* стан підтягуємо ТІЛЬКИ після з'єднання всього ланцюжка */
  for (guint i = 0; i < n; i++)
    gst_element_sync_state_with_parent (chain[i]);

  return gst_element_get_static_pad (chain[0], "sink");
}

/* Викликається в НИТЦІ ПОТОКУ uridecodebin, не в головній. */
static void on_pad_added (GstElement *dec, GstPad *pad, gpointer data)
{
  static const gchar *const video[] = { "queue", "videoconvert", "autovideosink", NULL };
  static const gchar *const audio[] = { "queue", "audioconvert", "audioresample",
                                        "autoaudiosink", NULL };
  App *app = data;

  GstCaps *caps = gst_pad_get_current_caps (pad);
  if (!caps)
    caps = gst_pad_query_caps (pad, NULL);
  const gchar *media = gst_structure_get_name (gst_caps_get_structure (caps, 0));

  const gchar *const *want = NULL;
  const gchar *label = NULL;
  if (g_str_has_prefix (media, "video/"))      { want = video; label = "відео"; }
  else if (g_str_has_prefix (media, "audio/")) { want = audio; label = "звук";  }
  gst_caps_unref (caps);            /* після цього рядка media вже недійсний */

  if (!want)
    return;                         /* субтитри й службові потоки не беремо */

  GstPad *sink = add_branch (app, want);
  if (!sink)
    return;
  if (gst_pad_link (pad, sink) != GST_PAD_LINK_OK)
    g_printerr ("гілку «%s» не приєднано\n", label);
  gst_object_unref (sink);
}
