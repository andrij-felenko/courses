/* 1. Спільний годинник: беремо час у процесу-постачальника */
GstClock *net = gst_net_client_clock_new ("net", "192.168.1.10", 8554, 0);
gst_clock_wait_for_sync (net, 30 * GST_SECOND);       /* без цього перші секунди — сміття */
gst_pipeline_use_clock (GST_PIPELINE (pipeline), net);

/* 2. Спільна точка відліку: конвеєр не має права перевибрати base_time */
gst_element_set_start_time (pipeline, GST_CLOCK_TIME_NONE);
gst_element_set_base_time (pipeline, agreed_base);    /* однакове число в усіх учасників */

gst_element_set_state (pipeline, GST_STATE_PLAYING);
