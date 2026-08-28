static const gchar *const VIDEO_TAIL[] = { "queue", "videoconvert",
                                           "autovideosink", NULL };
static const gchar *const AUDIO_TAIL[] = { "queue", "audioconvert",
                                           "audioresample", "autoaudiosink", NULL };

/* Ланцюжок елементів як один бін із привидним sink-падом. */
static GstElement *
make_tail (const gchar *const *names)
{
  GstElement *branch = gst_bin_new (NULL);
  GstElement *prev = NULL;

  for (int i = 0; names[i]; i++) {
    GstElement *e = gst_element_factory_make (names[i], NULL);

    if (!e) {
      g_printerr ("немає елемента %s\n", names[i]);
      gst_object_unref (branch);
      return NULL;
    }
    gst_bin_add (GST_BIN (branch), e);

    if (!prev) {
      GstPad *sink = gst_element_get_static_pad (e, "sink");
      gst_element_add_pad (branch, gst_ghost_pad_new ("sink", sink));
      gst_object_unref (sink);
    } else if (!gst_element_link (prev, e)) {
      g_printerr ("%s → %s не з'єдналися\n", names[i - 1], names[i]);
      gst_object_unref (branch);
      return NULL;
    }
    prev = e;
  }
  return branch;
}

static void
on_pad_added (GstElement *dec, GstPad *pad, gpointer data)
{
  App *app = data;
  GstCaps *caps = gst_pad_get_current_caps (pad);
  const gchar *const *names;
  const gchar *media;
  GstElement *branch;
  GstPad *sink;

  if (!caps)
    caps = gst_pad_query_caps (pad, NULL);   /* обидва виклики віддають володіння */
  media = gst_structure_get_name (gst_caps_get_structure (caps, 0));

  if (g_str_has_prefix (media, "video/x-raw"))
    names = VIDEO_TAIL;
  else if (g_str_has_prefix (media, "audio/x-raw"))
    names = AUDIO_TAIL;
  else {
    journal (app, "пад %s: %s — хвоста для такого немає", GST_PAD_NAME (pad), media);
    gst_caps_unref (caps);
    return;
  }

  branch = make_tail (names);
  if (branch) {
    gst_bin_add (GST_BIN (app->pipeline), branch);      /* 1. у конвеєр */
    gst_element_sync_state_with_parent (branch);        /* 2. догнати стан */
    sink = gst_element_get_static_pad (branch, "sink");
    if (gst_pad_link (pad, sink) == GST_PAD_LINK_OK) {  /* 3. і лише тепер лінк */
      g_atomic_int_inc (&app->n_branches);
      journal (app, "пад %s: %s → хвіст із %u елементів",
               GST_PAD_NAME (pad), media, g_strv_length ((gchar **) names));
    } else {
      g_printerr ("пад %s не приєднався\n", GST_PAD_NAME (pad));
    }
    gst_object_unref (sink);
  }
  gst_caps_unref (caps);
}
