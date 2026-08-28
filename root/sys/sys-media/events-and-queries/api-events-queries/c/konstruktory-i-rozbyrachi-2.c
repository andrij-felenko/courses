typedef enum {
  GST_SEEK_TYPE_NONE = 0,   /* цю межу не чіпати */
  GST_SEEK_TYPE_SET  = 1,   /* абсолютне значення */
  GST_SEEK_TYPE_END  = 2    /* відносно кінця; від'ємне значення — назад від кінця */
} GstSeekType;

GST_SEEK_FLAG_FLUSH        = 1 << 0   /* скинути конвеєр: миттєво, але з розривом */
GST_SEEK_FLAG_ACCURATE     = 1 << 1   /* точна позиція ціною повільного пошуку */
GST_SEEK_FLAG_KEY_UNIT     = 1 << 2   /* дозволено з'їхати на найближчий ключовий кадр */
GST_SEEK_FLAG_SEGMENT      = 1 << 3   /* дійшовши до stop, надіслати SEGMENT_DONE замість EOS */
GST_SEEK_FLAG_TRICKMODE    = 1 << 4   /* дозволено ламати якість заради швидкості */
GST_SEEK_FLAG_SNAP_BEFORE  = 1 << 5
GST_SEEK_FLAG_SNAP_AFTER   = 1 << 6
GST_SEEK_FLAG_INSTANT_RATE_CHANGE = 1 << 10  /* змінити лише темп, не рухаючи позицію */
