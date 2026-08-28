static GstCaps *
gst_demo_flip_fixate_caps (GstBaseTransform * base,
    GstPadDirection direction, GstCaps * caps, GstCaps * othercaps)
{
  GstDemoFlip *self = GST_DEMO_FLIP (base);
  GstStructure *ins, *outs;
  DemoFlipMode mode;
  gint w, h;

  GST_OBJECT_LOCK (self);
  mode = self->mode;
  GST_OBJECT_UNLOCK (self);

  /* othercaps наш: прийшов з transfer full. Лишаємо першу структуру
     (вона найбажаніша) і робимо її змінною. */
  othercaps = gst_caps_truncate (othercaps);
  othercaps = gst_caps_make_writable (othercaps);

  ins = gst_caps_get_structure (caps, 0);
  outs = gst_caps_get_structure (othercaps, 0);

  if (gst_structure_get_int (ins, "width", &w) &&
      gst_structure_get_int (ins, "height", &h)) {
    if (mode == DEMO_FLIP_RIGHT) {        /* поворот обов'язковий */
      gint t = w; w = h; h = t;
    }
    /* «Тримайся тотожності»: з усього дозволеного беремо те, що
       найближче до геометрії, за яку не доведеться платити. */
    gst_structure_fixate_field_nearest_int (outs, "width", w);
    gst_structure_fixate_field_nearest_int (outs, "height", h);
  }

  /* Решту полів — типовим правилом: перше значення списку,
     розумна точка діапазону. */
  return gst_caps_fixate (othercaps);
}
