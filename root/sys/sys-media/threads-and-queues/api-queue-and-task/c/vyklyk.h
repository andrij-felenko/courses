GstElement *q = gst_element_factory_make ("queue", "q0");

g_object_set (q,
    "max-size-buffers", (guint) 3,
    "max-size-bytes",   (guint) 0,
    "max-size-time",    (guint64) 0,          /* приведення ОБОВ'ЯЗКОВЕ */
    "leaky",            2,                    /* GST_QUEUE_LEAK_DOWNSTREAM */
    NULL);

guint level;
g_object_get (q, "current-level-buffers", &level, NULL);   /* безпечно з будь-якої нитки */
