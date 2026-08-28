gboolean   autoplug_continue_cb  (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  gpointer user_data);

GValueArray *autoplug_factories_cb (GstElement *bin, GstPad *pad, GstCaps *caps,
                                    gpointer user_data);

GValueArray *autoplug_sort_cb    (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  GValueArray *factories, gpointer user_data);

GstAutoplugSelectResult
           autoplug_select_cb    (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  GstElementFactory *factory, gpointer user_data);

gboolean   autoplug_query_cb     (GstElement *bin, GstPad *pad, GstElement *child,
                                  GstQuery *query, gpointer user_data);

void       unknown_type_cb       (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  gpointer user_data);

void       drained_cb            (GstElement *bin, gpointer user_data);
