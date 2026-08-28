typedef enum {
  GST_APP_LEAKY_TYPE_NONE,        /* не протікати: черга блокує (за замовчуванням) */
  GST_APP_LEAKY_TYPE_UPSTREAM,    /* викидати НОВІ буфери — ті, що приходять */
  GST_APP_LEAKY_TYPE_DOWNSTREAM   /* викидати СТАРІ буфери — ті, що вже в черзі */
} GstAppLeakyType;                /* з 1.20 в appsrc, з 1.28 в appsink */

typedef enum {
  GST_APP_STREAM_TYPE_STREAM,         /* перемотування неможливе — жива трансляція */
  GST_APP_STREAM_TYPE_SEEKABLE,       /* перемотування можливе, але повільне — дані з вебсервера */
  GST_APP_STREAM_TYPE_RANDOM_ACCESS   /* перемотування швидке — локальний файл */
} GstAppStreamType;
