static GstStateChangeReturn
my_filter_change_state (GstElement *element, GstStateChange transition)
{
  MyFilter *self = MY_FILTER (element);
  GstStateChangeReturn ret;

  /* угору — своє ПЕРЕД базовим класом: потоків ще немає */
  switch (transition) {
    case GST_STATE_CHANGE_NULL_TO_READY:
      if (!my_filter_open_device (self))
        return GST_STATE_CHANGE_FAILURE;
      break;
    case GST_STATE_CHANGE_READY_TO_PAUSED:
      my_filter_reset_stream_state (self);
      break;
    default:
      break;
  }

  ret = GST_ELEMENT_CLASS (parent_class)->change_state (element, transition);
  if (ret == GST_STATE_CHANGE_FAILURE)
    return ret;

  /* униз — своє ПІСЛЯ базового класу: потоки вже зупинені */
  switch (transition) {
    case GST_STATE_CHANGE_PAUSED_TO_READY:
      my_filter_free_stream_buffers (self);
      break;
    case GST_STATE_CHANGE_READY_TO_NULL:
      my_filter_close_device (self);
      break;
    default:
      break;
  }

  return ret;
}
