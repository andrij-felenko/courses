/* Типова обробка на місці всередині елемента */
static GstFlowReturn
transform_ip (GstBaseTransform * trans, GstBuffer * buf)
{
  GstMapInfo info;

  /* buf уже придатний до запису: basetransform подбав про це за нас,
     викликавши gst_buffer_make_writable перед transform_ip */
  if (!gst_buffer_map (buf, &info, GST_MAP_READWRITE))
    return GST_FLOW_ERROR;

  for (gsize i = 0; i < info.size; i++)
    info.data[i] = 255 - info.data[i];      /* інверсія яскравості */

  gst_buffer_unmap (buf, &info);            /* обов'язково, навіть на помилці */
  return GST_FLOW_OK;
}
