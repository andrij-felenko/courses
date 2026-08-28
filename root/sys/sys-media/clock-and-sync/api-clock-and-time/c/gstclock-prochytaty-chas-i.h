GstClock *clock = gst_element_get_clock (sink);   /* NULL, якщо конвеєр не в PAUSED/PLAYING */
GstClockTime now = gst_clock_get_time (clock);
GstClockID   id  = gst_clock_new_single_shot_id (clock, now + 20 * GST_MSECOND);

GstClockTimeDiff jitter;
GstClockReturn   res = gst_clock_id_wait (id, &jitter);

if (res == GST_CLOCK_EARLY)
  g_print ("мить уже минула на %" GST_STIME_FORMAT "\n", GST_STIME_ARGS (jitter));

gst_clock_id_unschedule (id);   /* з іншого потоку це й є спосіб розбудити чекальника */
gst_clock_id_unref (id);        /* одноразовий id придатний рівно на одне чекання */
gst_object_unref (clock);
