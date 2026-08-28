static void
on_pad_added (GstElement *demux, GstPad *newpad, gpointer user_data)
{
  App *app = user_data;

  /* Тип доріжки читаємо з caps самого пада: qtdemux виставляє їх ще до того,
     як оголосити пад. Якщо поточних caps немає — беремо те, що пад уміє. */
  GstCaps *caps = gst_pad_get_current_caps (newpad);
  if (caps == NULL)
    caps = gst_pad_query_caps (newpad, NULL);
  const gchar *media = gst_structure_get_name (gst_caps_get_structure (caps, 0));
  g_print ("новий пад %s: %s\n", GST_PAD_NAME (newpad), media);

  GstElement *branch = NULL;
  if (g_str_has_prefix (media, "video/") && app->video_branch == NULL) {
    branch = make_branch ("video-branch", VIDEO_BRANCH, &app->video_tail);
    if (branch != NULL) {
      app->video_branch = branch;
      app->video_pad = gst_object_ref (newpad);   /* пад у сигналі — позичений */
    }
  } else if (g_str_has_prefix (media, "audio/") && app->audio_branch == NULL) {
    branch = make_branch ("audio-branch", AUDIO_BRANCH, NULL);
    app->audio_branch = branch;
  }
  gst_caps_unref (caps);

  if (branch == NULL) {
    g_print ("  доріжку пропускаємо\n");
    return;
  }

  /* 1. Спершу в конвеєр: інакше пади не мають спільного предка
        і gst_pad_link поверне GST_PAD_LINK_WRONG_HIERARCHY. */
  gst_bin_add (GST_BIN (app->pipeline), branch);

  /* 2. Тепер з'єднання. */
  GstPad *branch_in = gst_element_get_static_pad (branch, "sink");
  GstPadLinkReturn ret = gst_pad_link (newpad, branch_in);
  gst_object_unref (branch_in);
  if (GST_PAD_LINK_FAILED (ret)) {
    g_printerr ("  не з'єдналося: %s\n", gst_pad_link_get_name (ret));
    return;
  }

  /* 3. Гілка щойно створена — вона в NULL, а конвеєр уже в PLAYING.
        Без цього рядка вона просто мовчатиме, і жодної помилки не буде. */
  if (!gst_element_sync_state_with_parent (branch))
    g_printerr ("  гілка не догнала стан конвеєра\n");
}
