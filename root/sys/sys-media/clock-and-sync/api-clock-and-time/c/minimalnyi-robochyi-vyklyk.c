#include <gst/gst.h>

typedef struct { GstSegment seg; GstElement *sink; } Ctx;

static GstPadProbeReturn
probe (GstPad * pad, GstPadProbeInfo * info, gpointer user_data)
{
  Ctx *ctx = user_data;

  if (GST_PAD_PROBE_INFO_TYPE (info) & GST_PAD_PROBE_TYPE_EVENT_DOWNSTREAM) {
    GstEvent *ev = GST_PAD_PROBE_INFO_EVENT (info);
    if (GST_EVENT_TYPE (ev) == GST_EVENT_SEGMENT)
      gst_event_copy_segment (ev, &ctx->seg);       /* сегмент потрібен для перекладу */
    return GST_PAD_PROBE_OK;
  }

  GstBuffer *buf = GST_PAD_PROBE_INFO_BUFFER (info);
  GstClockTime pts = GST_BUFFER_PTS (buf);

  if (!GST_CLOCK_TIME_IS_VALID (pts)) {
    g_print ("буфер без PTS — споживач покаже його одразу\n");
    return GST_PAD_PROBE_OK;
  }

  GstClockTime rt = gst_segment_to_running_time (&ctx->seg, GST_FORMAT_TIME, pts);
  GstClockTime base = gst_element_get_base_time (ctx->sink);
  GstClock *clock = gst_element_get_clock (ctx->sink);
  if (clock == NULL)                                 /* конвеєр ще не в PAUSED/PLAYING */
    return GST_PAD_PROBE_OK;

  GstClockTimeDiff late = GST_CLOCK_DIFF (rt + base, gst_clock_get_time (clock));
  gst_object_unref (clock);

  g_print ("PTS %" GST_TIME_FORMAT "   running %" GST_TIME_FORMAT
           "   запізнення %" GST_STIME_FORMAT "\n",
           GST_TIME_ARGS (pts), GST_TIME_ARGS (rt), GST_STIME_ARGS (late));
  return GST_PAD_PROBE_OK;
}

int
main (int argc, char *argv[])
{
  gst_init (&argc, &argv);

  GstElement *pipeline = gst_parse_launch
      ("videotestsrc is-live=true ! video/x-raw,framerate=25/1 ! "
       "videoconvert ! autovideosink name=out", NULL);
  GstElement *sink = gst_bin_get_by_name (GST_BIN (pipeline), "out");

  Ctx ctx = { 0 };
  gst_segment_init (&ctx.seg, GST_FORMAT_TIME);
  ctx.sink = sink;

  GstPad *pad = gst_element_get_static_pad (sink, "sink");
  gst_pad_add_probe (pad,
      GST_PAD_PROBE_TYPE_BUFFER | GST_PAD_PROBE_TYPE_EVENT_DOWNSTREAM,
      probe, &ctx, NULL);

  gst_element_set_state (pipeline, GST_STATE_PLAYING);
  GstMessage *msg = gst_bus_timed_pop_filtered (GST_ELEMENT_BUS (pipeline),
      10 * GST_SECOND, GST_MESSAGE_ERROR | GST_MESSAGE_EOS);
  if (msg)
    gst_message_unref (msg);

  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (pad);
  gst_object_unref (sink);
  gst_object_unref (pipeline);
  return 0;
}
