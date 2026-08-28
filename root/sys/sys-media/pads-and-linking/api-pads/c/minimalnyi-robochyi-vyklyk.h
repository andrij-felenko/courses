GstPad *tee_src = gst_element_request_pad_simple (tee, "src_%u");  /* створено, +1 */
GstPad *q_sink  = gst_element_get_static_pad (queue, "sink");      /* +1 */

if (GST_PAD_LINK_FAILED (gst_pad_link (tee_src, q_sink)))
  g_printerr ("гілка tee не під'єдналася\n");

/* … робота … */

gst_pad_unlink (tee_src, q_sink);
gst_object_unref (q_sink);                       /* посилання з get_static_pad */

gst_element_release_request_pad (tee, tee_src);  /* 1) сказати елементу */
gst_object_unref (tee_src);                      /* 2) віддати своє посилання */
