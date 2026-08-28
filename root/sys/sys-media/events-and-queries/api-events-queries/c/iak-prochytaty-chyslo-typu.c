#define GST_EVENT_NUM_SHIFT   (8)
#define GST_EVENT_MAKE_TYPE(num,flags)  (((num) << GST_EVENT_NUM_SHIFT) | (flags))

typedef enum {
  GST_EVENT_TYPE_UPSTREAM       = 1 << 0,   /* має право йти проти течії */
  GST_EVENT_TYPE_DOWNSTREAM     = 1 << 1,   /* має право йти за течією */
  GST_EVENT_TYPE_SERIALIZED     = 1 << 2,   /* стоїть у черзі разом із буферами */
  GST_EVENT_TYPE_STICKY         = 1 << 3,   /* осідає на паді */
  GST_EVENT_TYPE_STICKY_MULTI   = 1 << 4    /* осідає в кількох примірниках */
} GstEventTypeFlags;

#define GST_EVENT_TYPE_BOTH \
    ((GstEventTypeFlags)(GST_EVENT_TYPE_UPSTREAM | GST_EVENT_TYPE_DOWNSTREAM))
