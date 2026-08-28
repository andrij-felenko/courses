gboolean gst_element_link               (GstElement *src, GstElement *dest);
gboolean gst_element_link_many          (GstElement *e1, GstElement *e2, ...);  /* NULL-термінований */
gboolean gst_element_link_filtered      (GstElement *src, GstElement *dest,
                                         GstCaps *filter);
gboolean gst_element_link_pads          (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname);
gboolean gst_element_link_pads_full     (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname,
                                         GstPadLinkCheck flags);
gboolean gst_element_link_pads_filtered (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname,
                                         GstCaps *filter);
void     gst_element_unlink             (GstElement *src, GstElement *dest);
void     gst_element_unlink_many        (GstElement *e1, GstElement *e2, ...);
void     gst_element_unlink_pads        (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname);
