static gboolean
gst_demo_flip_get_unit_size (GstBaseTransform * base, GstCaps * caps,
    gsize * size)
{
  GstVideoInfo info;

  if (!gst_video_info_from_caps (&info, caps))
    return FALSE;

  *size = GST_VIDEO_INFO_SIZE (&info);   /* байтів на один кадр */
  return TRUE;
}

static GstFlowReturn
gst_demo_flip_transform (GstBaseTransform * base, GstBuffer * inbuf,
    GstBuffer * outbuf)
{
  GstDemoFlip *self = GST_DEMO_FLIP (base);
  GstVideoFrame src, dst;
  guint8 *sp, *dp;
  gint x, y, w, h, ss, ds;

  if (G_UNLIKELY (!self->negotiated)) {
    GST_ELEMENT_ERROR (self, CORE, NEGOTIATION, (NULL),
        ("кадр прийшов, а формату ще немає"));
    return GST_FLOW_NOT_NEGOTIATED;
  }

  if (!gst_video_frame_map (&src, &self->in_info, inbuf, GST_MAP_READ))
    return GST_FLOW_ERROR;
  if (!gst_video_frame_map (&dst, &self->out_info, outbuf, GST_MAP_WRITE)) {
    gst_video_frame_unmap (&src);
    return GST_FLOW_ERROR;
  }

  w = GST_VIDEO_FRAME_WIDTH (&src);
  h = GST_VIDEO_FRAME_HEIGHT (&src);
  sp = GST_VIDEO_FRAME_PLANE_DATA (&src, 0);
  dp = GST_VIDEO_FRAME_PLANE_DATA (&dst, 0);
  ss = GST_VIDEO_FRAME_PLANE_STRIDE (&src, 0);
  ds = GST_VIDEO_FRAME_PLANE_STRIDE (&dst, 0);

  /* Поворот за годинниковою: піксель (x, y) їде в (h-1-y, x). */
  for (y = 0; y < h; y++)
    for (x = 0; x < w; x++)
      dp[x * ds + (h - 1 - y)] = sp[y * ss + x];

  gst_video_frame_unmap (&dst);
  gst_video_frame_unmap (&src);
  return GST_FLOW_OK;
}
