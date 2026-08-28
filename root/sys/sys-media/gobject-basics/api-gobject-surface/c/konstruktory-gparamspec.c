GType
gst_my_enc_pass_get_type (void)
{
  static gsize id = 0;
  static const GEnumValue values[] = {
    { GST_MY_ENC_PASS_CBR,  "Constant Bitrate Encoding", "cbr"  },
    { GST_MY_ENC_PASS_QUANT, "Constant Quantizer",       "quant" },
    { 0, NULL, NULL }
  };
  if (g_once_init_enter (&id)) {
    GType t = g_enum_register_static ("GstMyEncPass", values);
    g_once_init_leave (&id, t);
  }
  return id;
}
