/* ── СПОЖИВАЧ: що я вимагаю від того, хто виділятиме ─────────────────── */
static gboolean
my_sink_propose_allocation (GstBaseSink * sink, GstQuery * query)
{
  GstCaps *caps;
  gboolean need_pool;
  GstVideoInfo info;
  GstAllocationParams params;

  gst_query_parse_allocation (query, &caps, &need_pool);
  if (caps == NULL || !gst_video_info_from_caps (&info, caps))
    return FALSE;

  /* «я розумію GstVideoMeta» — джерело може лишити свій крок рядка */
  gst_query_add_allocation_meta (query, GST_VIDEO_META_API_TYPE, NULL);

  /* вимоги мого заліза: рядок по 256 байтів, 64 байти запасу за кадром */
  gst_allocation_params_init (&params);
  params.align = 255;
  params.padding = 64;
  gst_query_add_allocation_param (query, NULL, &params);   /* алокатор — будь-який */

  if (need_pool) {
    GstBufferPool *pool = gst_video_buffer_pool_new ();
    GstStructure *config = gst_buffer_pool_get_config (pool);

    gst_buffer_pool_config_set_params (config, caps, GST_VIDEO_INFO_SIZE (&info), 4, 0);
    gst_buffer_pool_config_add_option (config, GST_BUFFER_POOL_OPTION_VIDEO_META);
    if (!gst_buffer_pool_set_config (pool, config)) {
      gst_object_unref (pool);
      return FALSE;
    }
    gst_query_add_allocation_pool (query, pool, GST_VIDEO_INFO_SIZE (&info), 4, 0);
    gst_object_unref (pool);            /* запит узяв власне посилання */
  }
  return TRUE;
}
