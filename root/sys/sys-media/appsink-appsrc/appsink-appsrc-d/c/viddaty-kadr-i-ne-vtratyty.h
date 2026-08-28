/* дані готує ваш код; звільнить їх release_frame, коли конвеєр
   відпустить останнє посилання на буфер — жодного копіювання */
GstBuffer *buf = gst_buffer_new_wrapped_full (
    GST_MEMORY_FLAG_READONLY, frame_data, frame_size, 0, frame_size,
    frame_owner, (GDestroyNotify) release_frame);

GST_BUFFER_PTS (buf)      = frame_index * GST_SECOND / 30;
GST_BUFFER_DURATION (buf) = GST_SECOND / 30;

GstFlowReturn ret = gst_app_src_push_buffer (GST_APP_SRC (src), buf);
/* buf уже НЕ ваш — навіть якщо ret не GST_FLOW_OK */
if (ret != GST_FLOW_OK)
  break;                 /* GST_FLOW_FLUSHING: конвеєр згортається */
