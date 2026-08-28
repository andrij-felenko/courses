/* Поміняти місцями width і height в одній структурі. */
static void
demo_flip_swap_wh (GstStructure * s)
{
  const GValue *w = gst_structure_get_value (s, "width");
  const GValue *h = gst_structure_get_value (s, "height");
  GValue tw = G_VALUE_INIT, th = G_VALUE_INIT;
  gint par_n, par_d;

  if (w == NULL || h == NULL)
    return;                       /* нема поля — нема обмеження */

  /* Копії обов'язкові: щойно ми запишемо перше поле, чужі
     вказівники всередину структури стають непевними. */
  g_value_init (&tw, G_VALUE_TYPE (w)); g_value_copy (w, &tw);
  g_value_init (&th, G_VALUE_TYPE (h)); g_value_copy (h, &th);
  gst_structure_set_value (s, "width", &th);
  gst_structure_set_value (s, "height", &tw);
  g_value_unset (&tw);
  g_value_unset (&th);

  /* Поворот на чверть оберту перевертає і співвідношення сторін
     пікселя. Якщо воно записане дробом — інвертуємо; якщо там
     діапазон чи список, чесніше зняти обмеження зовсім. */
  if (gst_structure_get_fraction (s, "pixel-aspect-ratio", &par_n, &par_d)) {
    if (par_n != par_d)
      gst_structure_set (s, "pixel-aspect-ratio",
          GST_TYPE_FRACTION, par_d, par_n, NULL);
  } else {
    gst_structure_remove_field (s, "pixel-aspect-ratio");
  }
}

static GstCaps *
gst_demo_flip_transform_caps (GstBaseTransform * base,
    GstPadDirection direction, GstCaps * caps, GstCaps * filter)
{
  GstDemoFlip *self = GST_DEMO_FLIP (base);
  DemoFlipMode mode;
  GstCaps *ret;
  guint i;

  GST_OBJECT_LOCK (self);
  mode = self->mode;
  GST_OBJECT_UNLOCK (self);

  if (mode == DEMO_FLIP_NONE) {
    /* Геометрія не міняється: з іншого боку годиться рівно те саме. */
    ret = gst_caps_ref (caps);
  } else {
    GstCaps *swapped = gst_caps_copy (caps);

    for (i = 0; i < gst_caps_get_size (swapped); i++)
      demo_flip_swap_wh (gst_caps_get_structure (swapped, i));

    if (mode == DEMO_FLIP_RIGHT) {
      ret = swapped;                    /* поворот неминучий */
    } else {
      /* auto: годиться і те, і те. Тотожність ставимо ПЕРШОЮ —
         порядок структур і є порядком переваги. */
      ret = gst_caps_copy (caps);
      gst_caps_append (ret, swapped);   /* append забирає swapped собі */
    }
  }

  /* Фільтр — не порада, а вимога. Той, хто питав, уже знає, що
     йому не потрібне, і не хоче отримати цього у відповіді. */
  if (filter) {
    GstCaps *tmp = gst_caps_intersect_full (filter, ret,
        GST_CAPS_INTERSECT_FIRST);
    gst_caps_unref (ret);
    ret = tmp;
  }

  GST_DEBUG_OBJECT (self, "%s: %" GST_PTR_FORMAT " крізь фільтр %"
      GST_PTR_FORMAT " → %" GST_PTR_FORMAT,
      direction == GST_PAD_SINK ? "sink→src" : "src→sink",
      caps, filter, ret);
  return ret;
}
