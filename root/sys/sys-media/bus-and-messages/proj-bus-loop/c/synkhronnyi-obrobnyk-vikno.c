#include <gst/video/videooverlay.h>

static guintptr window_handle;    /* заповнює віконна система до пуску конвеєра */

static GstBusSyncReply on_sync_message (GstBus *bus, GstMessage *msg, gpointer data)
{
  if (!gst_is_video_overlay_prepare_window_handle_message (msg))
    return GST_BUS_PASS;          /* решта — звичайним шляхом, у чергу */

  gst_video_overlay_set_window_handle (GST_VIDEO_OVERLAY (GST_MESSAGE_SRC (msg)),
                                       window_handle);
  gst_message_unref (msg);        /* DROP означає: повідомлення наше — нам і звільняти */
  return GST_BUS_DROP;
}

/* поруч із gst_bus_add_watch(), до першого set_state */
gst_bus_set_sync_handler (app.bus, on_sync_message, NULL, NULL);
