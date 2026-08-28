GstBufferPool *pool = gst_buffer_pool_new ();      /* або з елемента, або із запиту */
GstStructure  *config = gst_buffer_pool_get_config (pool);   /* окрема копія */

gst_buffer_pool_config_set_params (config, caps, size, min_buffers, max_buffers);
gst_buffer_pool_config_set_allocator (config, allocator, &params);
if (gst_buffer_pool_has_option (pool, GST_BUFFER_POOL_OPTION_VIDEO_META))
  gst_buffer_pool_config_add_option (config, GST_BUFFER_POOL_OPTION_VIDEO_META);

if (!gst_buffer_pool_set_config (pool, config))    /* config з'їдено в будь-якому разі */
  goto config_failed;

gst_buffer_pool_set_active (pool, TRUE);           /* саме тут виділяються min_buffers */

/* … робота … */
gst_buffer_pool_acquire_buffer (pool, &buf, NULL);
gst_buffer_unref (buf);                            /* повернення в пул */

gst_buffer_pool_set_active (pool, FALSE);          /* звільняє, коли всі буфери вдома */
gst_object_unref (pool);
