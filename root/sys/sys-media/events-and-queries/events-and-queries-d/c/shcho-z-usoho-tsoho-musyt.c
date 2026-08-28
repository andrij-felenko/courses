static gboolean
my_sink_event (GstPad *pad, GstObject *parent, GstEvent *event)
{
  MyFilter *self = MY_FILTER (parent);

  switch (GST_EVENT_TYPE (event)) {
    case GST_EVENT_SEGMENT:
      /* запам'ятовуємо систему координат часу для себе —
         і ОБОВ'ЯЗКОВО пускаємо подію далі: вона потрібна не лише нам */
      gst_event_copy_segment (event, &self->segment);
      break;

    case GST_EVENT_FLUSH_STOP:
      /* після скидання наш внутрішній стан недійсний */
      my_filter_reset (self);
      break;

    case GST_EVENT_CUSTOM_DOWNSTREAM:
      if (gst_event_has_name (event, "my-marker")) {
        my_filter_handle_marker (self, event);
        gst_event_unref (event);       /* з'їли — самі й звільняємо */
        return TRUE;
      }
      break;

    default:
      break;
  }

  /* усе інше — типовій обробці: вона розішле подію на всі src-пади */
  return gst_pad_event_default (pad, parent, event);
}
