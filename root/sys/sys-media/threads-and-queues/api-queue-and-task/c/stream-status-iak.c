static GstTaskPool *my_pool;              /* створений один раз при старті застосунку */

static GstBusSyncReply
sync_handler (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  if (GST_MESSAGE_TYPE (msg) != GST_MESSAGE_STREAM_STATUS)
    return GST_BUS_PASS;

  GstStreamStatusType type;
  GstElement *owner;
  gst_message_parse_stream_status (msg, &type, &owner);

  const GValue *val = gst_message_get_stream_status_object (msg);

  switch (type) {
    case GST_STREAM_STATUS_TYPE_CREATE: {
      GstTask *task = GST_TASK (g_value_get_object (val));
      gst_task_set_pool (task, my_pool);      /* нитки ще нема — саме час */
      break;
    }
    case GST_STREAM_STATUS_TYPE_ENTER:
      /* ми ВСЕРЕДИНІ нової нитки: пріоритет виставляють тільки звідси */
      set_thread_priority_for_self ();
      break;
    default:
      break;
  }
  return GST_BUS_PASS;                        /* хай іде далі, у звичайне стеження */
}

GstBus *bus = gst_element_get_bus (pipeline);
gst_bus_set_sync_handler (bus, sync_handler, NULL, NULL);
gst_object_unref (bus);
