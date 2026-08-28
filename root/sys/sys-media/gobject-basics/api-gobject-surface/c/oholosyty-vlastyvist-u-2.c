static void
gst_my_enc_set_property (GObject * object, guint prop_id,
    const GValue * value, GParamSpec * pspec)
{
  GstMyEnc *self = GST_MY_ENC (object);

  switch (prop_id) {
    case PROP_BITRATE:
      GST_OBJECT_LOCK (self);                    /* нитка потоку читає це поле */
      self->bitrate = g_value_get_uint (value);
      GST_OBJECT_UNLOCK (self);
      break;
    case PROP_LOCATION:
      GST_OBJECT_LOCK (self);
      g_free (self->location);
      self->location = g_value_dup_string (value);  /* dup, а не get: рядок наш */
      GST_OBJECT_UNLOCK (self);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
  }
}
