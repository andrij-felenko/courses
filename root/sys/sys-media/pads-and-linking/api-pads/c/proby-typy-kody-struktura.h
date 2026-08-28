struct _GstPadProbeInfo {
  GstPadProbeType type;
  gulong          id;
  gpointer        data;
  guint64         offset;
  guint           size;
};

#define GST_PAD_PROBE_INFO_TYPE(d)        ((d)->type)
#define GST_PAD_PROBE_INFO_ID(d)          ((d)->id)
#define GST_PAD_PROBE_INFO_DATA(d)        ((d)->data)
#define GST_PAD_PROBE_INFO_FLOW_RETURN(d) ((d)->ABI.abi.flow_ret)

GstBuffer     *gst_pad_probe_info_get_buffer      (GstPadProbeInfo *info);
GstBufferList *gst_pad_probe_info_get_buffer_list (GstPadProbeInfo *info);
GstEvent      *gst_pad_probe_info_get_event       (GstPadProbeInfo *info);
GstQuery      *gst_pad_probe_info_get_query       (GstPadProbeInfo *info);
