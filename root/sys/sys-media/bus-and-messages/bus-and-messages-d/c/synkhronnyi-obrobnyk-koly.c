static GstBusSyncReply on_sync_message (GstBus *bus, GstMessage *msg, gpointer data)
{
  if (!gst_is_video_overlay_prepare_window_handle_message (msg))
    return GST_BUS_PASS;              /* решта — звичайним шляхом, у головний цикл */

  gst_video_overlay_set_window_handle (GST_VIDEO_OVERLAY (GST_MESSAGE_SRC (msg)),
                                       (guintptr) window_id);
  gst_message_unref (msg);            /* DROP означає: повідомлення наше — нам і звільняти */
  return GST_BUS_DROP;
}
