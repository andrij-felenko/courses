static void
my_loop (gpointer user_data)             /* виконується під замком потоку */
{
  GstPad *pad = user_data;
  MyElement *self = MY_ELEMENT (gst_pad_get_parent (pad));
  GstBuffer *buf = NULL;

  GstFlowReturn ret = gst_pad_pull_range (self->sinkpad, self->offset, 4096, &buf);
  if (ret != GST_FLOW_OK) {
    gst_pad_pause_task (pad);            /* спиняємо СЕБЕ саме так */
    goto done;
  }
  self->offset += gst_buffer_get_size (buf);

  if (gst_pad_push (pad, buf) != GST_FLOW_OK)
    gst_pad_pause_task (pad);

done:
  gst_object_unref (self);
}

static gboolean
my_activate_mode (GstPad *pad, GstObject *parent, GstPadMode mode, gboolean active)
{
  if (mode != GST_PAD_MODE_PULL)
    return FALSE;                        /* у режимі штовхання нитки тут не буде */

  return active ? gst_pad_start_task (pad, my_loop, pad, NULL)
                : gst_pad_stop_task (pad);
}
