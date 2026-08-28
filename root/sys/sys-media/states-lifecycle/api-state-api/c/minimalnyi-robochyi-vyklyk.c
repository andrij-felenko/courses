#include <gst/gst.h>

static gboolean
await_state (GstElement *pipeline, GstState want)
{
  GstBus *bus = gst_element_get_bus (pipeline);
  GstStateChangeReturn ret = gst_element_set_state (pipeline, want);
  gboolean ok = FALSE;

  switch (ret) {
    case GST_STATE_CHANGE_SUCCESS:
      ok = TRUE;                    /* стан уже досягнуто */
      break;

    case GST_STATE_CHANGE_NO_PREROLL:
      ok = TRUE;                    /* живий конвеєр: ASYNC_DONE не буде ніколи */
      break;

    case GST_STATE_CHANGE_ASYNC: {
      /* єдиний ASYNC_DONE, який доходить сюди, — від самого конвеєра */
      GstMessage *msg = gst_bus_timed_pop_filtered (bus, 5 * GST_SECOND,
          GST_MESSAGE_ASYNC_DONE | GST_MESSAGE_ERROR);

      if (msg == NULL) {
        g_printerr ("перехід не завершився за 5 с — конвеєр застряг\n");
      } else {
        ok = (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ASYNC_DONE);
        if (!ok) {
          GError *err = NULL;
          gchar *dbg = NULL;
          gst_message_parse_error (msg, &err, &dbg);
          g_printerr ("%s: %s (%s)\n",
              GST_OBJECT_NAME (GST_MESSAGE_SRC (msg)),
              err->message, dbg ? dbg : "без подробиць");
          g_clear_error (&err);
          g_free (dbg);
        }
        gst_message_unref (msg);
      }
      break;
    }

    case GST_STATE_CHANGE_FAILURE:
      break;                        /* причина приїде окремим ERROR */
  }

  if (!ok)                          /* єдина коректна реакція на невдачу */
    gst_element_set_state (pipeline, GST_STATE_NULL);

  gst_object_unref (bus);
  return ok;
}
