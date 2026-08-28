/* спрощена до суті, але справжня логіка queue */

static GstFlowReturn
queue_chain (GstPad *pad, GstObject *parent, GstBuffer *buf)
{
  GstQueue *q = GST_QUEUE (parent);          /* виконується в НИТЦІ ВЕРХНЬОГО сусіда */

  g_mutex_lock (&q->qlock);
  while (queue_is_full (q) && !q->flushing) {
    q->waiting_del = TRUE;
    g_cond_wait (&q->item_del, &q->qlock);   /* доки нижня нитка не забере */
  }
  if (q->flushing) {                          /* прокинулися через FLUSH_START */
    g_mutex_unlock (&q->qlock);
    gst_buffer_unref (buf);
    return GST_FLOW_FLUSHING;
  }
  gst_queue_array_push_tail (q->queue, buf); /* власність буфера перейшла черзі */
  g_cond_signal (&q->item_add);              /* розбудити власну нитку */

  GstFlowReturn ret = q->srcresult;          /* що ОСТАННЄ сказали знизу */
  g_mutex_unlock (&q->qlock);
  return ret;                                /* це почує верхній сусід */
}

static void
queue_loop (GstPad *pad)                     /* крутиться у ВЛАСНІЙ нитці */
{
  GstQueue *q = GST_QUEUE (gst_pad_get_parent (pad));

  g_mutex_lock (&q->qlock);
  while (queue_is_empty (q) && !q->flushing)
    g_cond_wait (&q->item_add, &q->qlock);
  if (q->flushing) {
    g_mutex_unlock (&q->qlock);
    gst_pad_pause_task (pad);
    return;
  }
  GstBuffer *buf = gst_queue_array_pop_head (q->queue);
  g_cond_signal (&q->item_del);              /* нагорі звільнилося місце */
  g_mutex_unlock (&q->qlock);

  q->srcresult = gst_pad_push (q->srcpad, buf);
  if (q->srcresult != GST_FLOW_OK)
    gst_pad_pause_task (pad);                /* далі нема куди — спиняємо нитку */
}
