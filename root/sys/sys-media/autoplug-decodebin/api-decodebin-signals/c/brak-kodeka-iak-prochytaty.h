gboolean gst_is_missing_plugin_message                (GstMessage *msg);
/* обидва — transfer full, звільняти через g_free() */
gchar *  gst_missing_plugin_message_get_description   (GstMessage *msg);
gchar *  gst_missing_plugin_message_get_installer_detail (GstMessage *msg);

/* створити таке саме повідомлення самому — знадобиться у власному елементі */
GstMessage *gst_missing_decoder_message_new    (GstElement *element,
                                                const GstCaps *decode_caps);
GstMessage *gst_missing_encoder_message_new    (GstElement *element,
                                                const GstCaps *encode_caps);
GstMessage *gst_missing_element_message_new    (GstElement *element,
                                                const gchar *factory_name);
GstMessage *gst_missing_uri_source_message_new (GstElement *element,
                                                const gchar *protocol);
GstMessage *gst_missing_uri_sink_message_new   (GstElement *element,
                                                const gchar *protocol);
