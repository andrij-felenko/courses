static gboolean
my_filter_sink_event (GstPad *pad, GstObject *parent, GstEvent *event)
{
  MyFilter *self = MY_FILTER (parent);

  switch (GST_EVENT_TYPE (event)) {
    case GST_EVENT_FLUSH_START:
      /* прийшла поза чергою, буфери ще в дорозі:
         тут можна лише розблокувати власні чекання, чіпати дані ще рано */
      g_atomic_int_set (&self->flushing, TRUE);
      my_filter_wake_up_waiters (self);
      break;

    case GST_EVENT_FLUSH_STOP:
      /* серіалізована: усе старе вже позаду, нове ще не пішло —
         єдина безпечна мить, щоб викинути накопичене */
      GST_OBJECT_LOCK (self);
      my_filter_drop_accumulated (self);          /* напівзібраний кадр, історія */
      gst_segment_init (&self->segment, GST_FORMAT_UNDEFINED);
      self->need_segment = TRUE;                  /* далі чекаємо на новий */
      GST_OBJECT_UNLOCK (self);
      g_atomic_int_set (&self->flushing, FALSE);
      break;

    case GST_EVENT_SEGMENT:
      /* нове правило перекладу міток; без нього мітки буферів безадресні */
      GST_OBJECT_LOCK (self);
      gst_event_copy_segment (event, &self->segment);
      self->need_segment = FALSE;
      GST_OBJECT_UNLOCK (self);
      break;

    default:
      break;
  }

  return gst_pad_event_default (pad, parent, event);
}
