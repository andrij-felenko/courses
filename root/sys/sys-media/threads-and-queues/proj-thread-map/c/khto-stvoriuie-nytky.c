/* Синхронний обробник шини: виконується в нитці ТОГО, ХТО ПОСТИТЬ
   повідомлення. Саме тому тут видно різницю між тим, хто задачу
   створює, і тим, хто в неї входить. */
static GstBusSyncReply
on_message_sync (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_STREAM_STATUS) {
    GstStreamStatusType type;
    GstElement *owner = NULL;
    const GValue *val;
    GstTask *task = NULL;
    const gchar *word = NULL;

    gst_message_parse_stream_status (msg, &type, &owner);
    val = gst_message_get_stream_status_object (msg);
    if (val != NULL && G_VALUE_TYPE (val) == GST_TYPE_TASK)
      task = g_value_get_object (val);

    switch (type) {
      case GST_STREAM_STATUS_TYPE_CREATE:
        word = "CREATE";
        /* ЄДИНИЙ момент, коли можна підсунути власний пул ниток:
             gst_task_set_pool (task, my_pool);
           після повернення звідси задача вже візьме типовий. */
        break;
      case GST_STREAM_STATUS_TYPE_ENTER:
        word = "ENTER";
        /* ми вже ВСЕРЕДИНІ нової нитки — тут виставляють пріоритет:
             struct sched_param p = { .sched_priority = 10 };
             pthread_setschedparam (pthread_self (), SCHED_RR, &p); */
        break;
      case GST_STREAM_STATUS_TYPE_LEAVE:
        word = "LEAVE";
        break;
      default:
        break;
    }

    if (word != NULL) {
      g_mutex_lock (&log_lock);
      g_print ("  [%-6s] задача «%s» від «%s» — ми зараз у T%d\n", word,
               task  ? GST_OBJECT_NAME (task)  : "?",
               owner ? GST_OBJECT_NAME (owner) : "?",
               thread_number (g_thread_self ()));
      g_mutex_unlock (&log_lock);
    }
  }
  return GST_BUS_PASS;   /* нічого не ковтаємо: далі повідомлення йде як завжди */
}
