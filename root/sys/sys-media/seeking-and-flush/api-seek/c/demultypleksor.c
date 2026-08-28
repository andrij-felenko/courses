static gboolean
my_demux_handle_seek (MyDemux *self, GstEvent *event)
{
  gdouble rate;
  GstFormat format;
  GstSeekFlags flags;
  GstSeekType start_type, stop_type;
  gint64 start, stop;
  gboolean flush, update;

  gst_event_parse_seek (event, &rate, &format, &flags,
      &start_type, &start, &stop_type, &stop);

  if (format != GST_FORMAT_TIME)          /* ми розуміємо лише час */
    return FALSE;

  flush = (flags & GST_SEEK_FLAG_FLUSH) != 0;

  /* 1. розчистити дорогу: обидва напрямки, поза чергою */
  if (flush) {
    gst_pad_push_event (self->sinkpad, gst_event_new_flush_start ());
    gst_pad_push_event (self->srcpad,  gst_event_new_flush_start ());
  } else {
    gst_pad_pause_task (self->sinkpad); /* нефлашний: просто спинити завдання */
  }

  /* 2. дочекатися, доки потік обробки справді вийде: замок вільний
        лише тоді, коли ніхто не всередині ланцюжкової функції */
  GST_PAD_STREAM_LOCK (self->sinkpad);

  /* 3. застосувати подію до свого сегмента й знайти байтове зміщення */
  gst_segment_do_seek (&self->segment, rate, format, flags,
      start_type, start, stop_type, stop, &update);

  if (update)
    self->byte_offset = my_demux_index_lookup (self, self->segment.start);

  /* 4. відпустити пади й оголосити новий сегмент */
  if (flush) {
    gst_pad_push_event (self->sinkpad, gst_event_new_flush_stop (TRUE));
    gst_pad_push_event (self->srcpad,  gst_event_new_flush_stop (TRUE));
  }
  self->need_segment = TRUE;              /* SEGMENT піде перед першим буфером */

  /* 5. пустити дані */
  gst_pad_start_task (self->sinkpad,
      (GstTaskFunction) my_demux_loop, self, NULL);

  GST_PAD_STREAM_UNLOCK (self->sinkpad);
  return TRUE;
}
