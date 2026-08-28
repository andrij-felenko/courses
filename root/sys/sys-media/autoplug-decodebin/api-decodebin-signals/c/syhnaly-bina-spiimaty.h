void element_added_cb        (GstBin *bin, GstElement *element,
                              gpointer user_data);
void element_removed_cb      (GstBin *bin, GstElement *element,
                              gpointer user_data);

/* з 1.10 — бачить і те, що додали у вкладені біни */
void deep_element_added_cb   (GstBin *bin, GstBin *sub_bin, GstElement *element,
                              gpointer user_data);
void deep_element_removed_cb (GstBin *bin, GstBin *sub_bin, GstElement *element,
                              gpointer user_data);
