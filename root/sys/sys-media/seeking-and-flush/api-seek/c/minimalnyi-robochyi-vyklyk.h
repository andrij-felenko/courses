/* перший захід: флашний, бо треба стрибнути на початок відрізка */
gst_element_seek (pipeline, 1.0, GST_FORMAT_TIME,
    GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_SEGMENT | GST_SEEK_FLAG_ACCURATE,
    GST_SEEK_TYPE_SET, 10 * GST_SECOND,
    GST_SEEK_TYPE_SET, 20 * GST_SECOND);

/* у відповідь на SEGMENT_DONE: той самий відрізок, але БЕЗ флаша */
gst_element_seek (pipeline, 1.0, GST_FORMAT_TIME,
    GST_SEEK_FLAG_SEGMENT | GST_SEEK_FLAG_ACCURATE,
    GST_SEEK_TYPE_SET, 10 * GST_SECOND,
    GST_SEEK_TYPE_SET, 20 * GST_SECOND);
