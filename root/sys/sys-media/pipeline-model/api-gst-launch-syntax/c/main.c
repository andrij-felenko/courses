#include <gst/gst.h>

int main (int argc, char *argv[])
{
  gst_init (&argc, &argv);

  GError *err = NULL;
  GstElement *pipeline = gst_parse_launch (
      "videotestsrc num-buffers=300 name=src "
      "! video/x-raw,width=1280,height=720,framerate=30/1 "
      "! videoconvert ! autovideosink",
      &err);

  /* УВАГА: err може бути виставлено й тоді, коли конвеєр повернувся —
     це «часткова» помилка, конвеєр зібрано не цілком. */
  if (err != NULL) {
    g_printerr ("розбір: %s\n", err->message);
    g_clear_error (&err);
  }
  if (pipeline == NULL)
    return 1;

  /* саме заради цього рядка елементам дають name= */
  GstElement *src = gst_bin_get_by_name (GST_BIN (pipeline), "src");
  g_object_set (src, "pattern", 18, NULL);   /* ball */
  gst_object_unref (src);

  gst_element_set_state (pipeline, GST_STATE_PLAYING);
  /* ... тут програма слухає шину ... */
  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (pipeline);
  return 0;
}
