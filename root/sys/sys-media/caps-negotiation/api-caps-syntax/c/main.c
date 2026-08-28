#include <gst/gst.h>

int
main (int argc, char **argv)
{
  gst_init (&argc, &argv);

  /* що вміє віддати джерело */
  GstCaps *src = gst_caps_from_string (
      "video/x-raw, format={ NV12, YUY2 }, width=[ 320, 1920 ], "
      "height=[ 240, 1080 ], framerate=[ 1/1, 60/1 ]");

  /* що приймає кодер; поля framerate НЕМА навмисно — йому байдуже */
  GstCaps *sink = gst_caps_new_simple ("video/x-raw",
      "format", G_TYPE_STRING, "NV12",
      "width",  GST_TYPE_INT_RANGE, 16, 4096,
      "height", GST_TYPE_INT_RANGE, 16, 4096,
      NULL);

  /* перевагу лишаємо за джерелом — тому воно перший аргумент */
  GstCaps *both = gst_caps_intersect_full (src, sink, GST_CAPS_INTERSECT_FIRST);
  if (gst_caps_is_empty (both)) {
    g_printerr ("спільного формату немає — тут і виникає not-negotiated\n");
    return 1;
  }

  gchar *s = gst_caps_to_string (both);
  g_print ("перетин: %s\n", s);          /* усе ще множина */
  g_free (s);

  /* fixate забирає посилання, тому даємо йому власне: caps скопіюються */
  GstCaps *fixed = gst_caps_fixate (gst_caps_ref (both));
  g_assert (gst_caps_is_fixed (fixed));

  const GstStructure *st = gst_caps_get_structure (fixed, 0);
  const gchar *fmt = gst_structure_get_string (st, "format");
  gint w = 0, h = 0, num = 0, den = 1;
  gst_structure_get_int (st, "width", &w);
  gst_structure_get_int (st, "height", &h);
  gst_structure_get_fraction (st, "framerate", &num, &den);
  g_print ("обрано: %s %dx%d @ %d/%d\n", fmt, w, h, num, den);

  gst_caps_unref (fixed);
  gst_caps_unref (both);
  gst_caps_unref (sink);
  gst_caps_unref (src);
  return 0;
}
