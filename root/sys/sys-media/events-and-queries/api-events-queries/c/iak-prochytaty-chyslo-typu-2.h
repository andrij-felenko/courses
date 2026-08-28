#define GST_QUERY_NUM_SHIFT   (8)
#define GST_QUERY_MAKE_TYPE(num,flags)  (((num) << GST_QUERY_NUM_SHIFT) | (flags))

typedef enum {
  GST_QUERY_TYPE_UPSTREAM   = 1 << 0,
  GST_QUERY_TYPE_DOWNSTREAM = 1 << 1,
  GST_QUERY_TYPE_SERIALIZED = 1 << 2
} GstQueryTypeFlags;

const gchar *      gst_query_type_get_name  (GstQueryType type);
GstQueryTypeFlags  gst_query_type_get_flags (GstQueryType type);
