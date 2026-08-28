/* Довести конвеєр до PAUSED. */
static gboolean
bring_to_paused (Player *p)
{
  GstStateChangeReturn r = gst_element_set_state (p->pipeline, GST_STATE_PAUSED);

  if (r == GST_STATE_CHANGE_FAILURE)
    return FALSE;
  if (r == GST_STATE_CHANGE_NO_PREROLL) {
    g_printerr ("джерело живе: перемотувати нема чого\n");
    return FALSE;
  }
  /* блокувальне чекання доречне саме тут: обслуговувати ще нема чого */
  return gst_element_get_state (p->pipeline, NULL, NULL,
                                SEEK_TIMEOUT) == GST_STATE_CHANGE_SUCCESS;
}
