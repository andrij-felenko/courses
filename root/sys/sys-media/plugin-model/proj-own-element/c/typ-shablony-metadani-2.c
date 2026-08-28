static gboolean
gst_my_filter_set_caps (GstBaseTransform * base, GstCaps * incaps,
    GstCaps * outcaps)
{
  GstMyFilter *self = GST_MY_FILTER (base);

  if (!gst_video_info_from_caps (&self->info, incaps)) {
    GST_ERROR_OBJECT (self, "не розібрав caps %" GST_PTR_FORMAT, incaps);
    return FALSE;
  }
  return TRUE;
}

static GstFlowReturn
gst_my_filter_transform_ip (GstBaseTransform * base, GstBuffer * buf)
{
  GstMyFilter *self = GST_MY_FILTER (base);
  GstVideoFrame frame;
  guint8 *plane;
  gint stride, w, h, x, y;

  if (!gst_video_frame_map (&frame, &self->info, buf, GST_MAP_READWRITE))
    return GST_FLOW_ERROR;

  plane = GST_VIDEO_FRAME_PLANE_DATA (&frame, 0);
  stride = GST_VIDEO_FRAME_PLANE_STRIDE (&frame, 0);
  w = GST_VIDEO_FRAME_WIDTH (&frame);
  h = GST_VIDEO_FRAME_HEIGHT (&frame);

  for (y = 0; y < h; y++) {
    guint8 *row = plane + (gsize) y * stride;
    for (x = 0; x < w; x++)
      row[x] = 255 - row[x];
  }

  gst_video_frame_unmap (&frame);
  return GST_FLOW_OK;
}
