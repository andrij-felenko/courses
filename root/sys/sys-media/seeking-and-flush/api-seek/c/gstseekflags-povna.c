typedef enum {
  GST_SEEK_FLAG_NONE                        = 0,
  GST_SEEK_FLAG_FLUSH                       = (1 << 0),
  GST_SEEK_FLAG_ACCURATE                    = (1 << 1),
  GST_SEEK_FLAG_KEY_UNIT                    = (1 << 2),
  GST_SEEK_FLAG_SEGMENT                     = (1 << 3),
  GST_SEEK_FLAG_TRICKMODE                   = (1 << 4),
  GST_SEEK_FLAG_SKIP                        = (1 << 4),
  GST_SEEK_FLAG_SNAP_BEFORE                 = (1 << 5),
  GST_SEEK_FLAG_SNAP_AFTER                  = (1 << 6),
  GST_SEEK_FLAG_SNAP_NEAREST                = GST_SEEK_FLAG_SNAP_BEFORE |
                                              GST_SEEK_FLAG_SNAP_AFTER,
  GST_SEEK_FLAG_TRICKMODE_KEY_UNITS         = (1 << 7),
  GST_SEEK_FLAG_TRICKMODE_NO_AUDIO          = (1 << 8),
  GST_SEEK_FLAG_TRICKMODE_FORWARD_PREDICTED = (1 << 9),
  GST_SEEK_FLAG_INSTANT_RATE_CHANGE         = (1 << 10),
} GstSeekFlags;
