/* gstutils.h — найкоротший шлях */
gboolean   gst_element_seek_simple (GstElement   *element,
                                    GstFormat     format,
                                    GstSeekFlags  seek_flags,
                                    gint64        seek_pos);

/* gstelement.h — повний контроль */
gboolean   gst_element_seek        (GstElement   *element,
                                    gdouble       rate,
                                    GstFormat     format,
                                    GstSeekFlags  flags,
                                    GstSeekType   start_type, gint64 start,
                                    GstSeekType   stop_type,  gint64 stop);

/* gstevent.h — коли подію треба потримати в руках */
GstEvent * gst_event_new_seek      (gdouble       rate,
                                    GstFormat     format,
                                    GstSeekFlags  flags,
                                    GstSeekType   start_type, gint64 start,
                                    GstSeekType   stop_type,  gint64 stop);
void       gst_event_parse_seek    (GstEvent     *event,
                                    gdouble      *rate,
                                    GstFormat    *format,
                                    GstSeekFlags *flags,
                                    GstSeekType  *start_type, gint64 *start,
                                    GstSeekType  *stop_type,  gint64 *stop);

gboolean   gst_element_send_event  (GstElement *element, GstEvent *event);
gboolean   gst_pad_send_event      (GstPad     *pad,     GstEvent *event);
