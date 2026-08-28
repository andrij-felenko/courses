static gboolean
gst_demo_flip_set_caps (GstBaseTransform * base,
    GstCaps * incaps, GstCaps * outcaps)
{
  GstDemoFlip *self = GST_DEMO_FLIP (base);
  GstVideoInfo in, out;

  self->negotiated = FALSE;

  if (!gst_video_info_from_caps (&in, incaps) ||
      !gst_video_info_from_caps (&out, outcaps))
    goto bad_caps;

  if (in.width == out.width && in.height == out.height)
    self->rotate = FALSE;
  else if (in.width == out.height && in.height == out.width)
    self->rotate = TRUE;
  else
    goto bad_caps;              /* такої пари ми не вміємо */

  self->in_info = in;
  self->out_info = out;
  self->negotiated = TRUE;

  /* Якщо робити нічого — хай базовий клас навіть не кличе нас
     на кадрах, а пропускає буфери повз. */
  gst_base_transform_set_passthrough (base, !self->rotate);

  GST_INFO_OBJECT (self, "узгоджено %dx%d → %dx%d, %s",
      in.width, in.height, out.width, out.height,
      self->rotate ? "поворот" : "наскрізний режим");
  return TRUE;

bad_caps:
  GST_ERROR_OBJECT (self, "пара, якої не буває: %" GST_PTR_FORMAT
      " → %" GST_PTR_FORMAT, incaps, outcaps);
  return FALSE;
}
