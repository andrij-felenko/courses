GstEvent *seek = gst_event_new_seek (1.0, GST_FORMAT_TIME,
                                     GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_KEY_UNIT,
                                     GST_SEEK_TYPE_SET, 10 * GST_SECOND,
                                     GST_SEEK_TYPE_NONE, GST_CLOCK_TIME_NONE);
guint32 sn = gst_util_seqnum_next ();
gst_event_set_seqnum (seek, sn);

if (!gst_element_send_event (pipeline, seek))     /* seek уже з'їдено */
  g_printerr ("перемотування не взяв ніхто\n");
/* gst_event_unref (seek) тут БУЛО Б помилкою */
