struct _GstBuffer {
  GstMiniObject          mini_object;
  guint8                *data;         /* вказівник на байти */
  guint                  size;         /* скільки їх */
  GstClockTime           timestamp;
  GstClockTime           duration;
  GstCaps               *caps;         /* формат — просто в буфері */
  guint64                offset;
  guint64                offset_end;
  guint8                *malloc_data;  /* що звільняти */
  GFreeFunc              free_func;    /* чим звільняти */
  GstBuffer             *parent;       /* чий я суббуфер */
  gpointer _gst_reserved[GST_PADDING - 2];
};
