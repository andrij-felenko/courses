/* Замість негайного call_async у пробі IDLE: проштовхнути EOS у голову гілки
   й дочекатися, поки він дійде до її хвоста. */
static GstPadProbeReturn
on_branch_drained (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  if (GST_EVENT_TYPE (GST_PAD_PROBE_INFO_DATA (info)) != GST_EVENT_EOS)
    return GST_PAD_PROBE_PASS;             /* решту подій пропускаємо далі */

  App *app = user_data;
  gst_pad_remove_probe (pad, GST_PAD_PROBE_INFO_ID (info));
  gst_element_call_async (app->pipeline, teardown_video_branch, app, NULL);
  return GST_PAD_PROBE_OK;                 /* хай приймач теж дізнається про кінець */
}

/* … у тілі on_pad_idle, одразу після gst_pad_unlink: */
GstPad *tail = gst_element_get_static_pad (app->video_tail, "sink");
gst_pad_add_probe (tail, GST_PAD_PROBE_TYPE_BLOCK | GST_PAD_PROBE_TYPE_EVENT_DOWNSTREAM,
                   on_branch_drained, app, NULL);
gst_object_unref (tail);
gst_pad_send_event (branch_in, gst_event_new_eos ());   /* EOS у голову гілки */
