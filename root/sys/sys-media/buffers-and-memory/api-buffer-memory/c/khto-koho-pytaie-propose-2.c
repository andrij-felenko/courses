/* ── ТОЙ, ХТО ВИДІЛЯЄ: обираю пул із зібраних відповідей ─────────────── */
static gboolean
my_src_decide_allocation (GstBaseSrc * src, GstQuery * query)
{
  GstBufferPool *pool = NULL;
  GstStructure *config;
  GstCaps *caps;
  guint size = 0, min = 0, max = 0;
  gboolean had_pool;

  gst_query_parse_allocation (query, &caps, NULL);

  had_pool = gst_query_get_n_allocation_pools (query) > 0;
  if (had_pool)
    gst_query_parse_nth_allocation_pool (query, 0, &pool, &size, &min, &max);

  if (pool == NULL) {                   /* ніхто нічого не запропонував */
    pool = gst_video_buffer_pool_new ();
    size = MAX (size, own_frame_size (src));
    min = 3;
    max = 0;
  }

  config = gst_buffer_pool_get_config (pool);
  gst_buffer_pool_config_set_params (config, caps, size, min, max);
  if (gst_query_find_allocation_meta (query, GST_VIDEO_META_API_TYPE, NULL))
    gst_buffer_pool_config_add_option (config, GST_BUFFER_POOL_OPTION_VIDEO_META);
  gst_buffer_pool_set_config (pool, config);

  /* рішення треба покласти назад у запит — базовий клас активує саме цей пул */
  if (had_pool)
    gst_query_set_nth_allocation_pool (query, 0, pool, size, min, max);
  else
    gst_query_add_allocation_pool (query, pool, size, min, max);

  gst_object_unref (pool);
  return TRUE;
}
