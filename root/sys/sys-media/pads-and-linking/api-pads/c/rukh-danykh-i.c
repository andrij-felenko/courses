typedef enum {
  GST_FLOW_CUSTOM_SUCCESS_2 =  102,
  GST_FLOW_CUSTOM_SUCCESS_1 =  101,
  GST_FLOW_CUSTOM_SUCCESS   =  100,
  GST_FLOW_OK               =    0,
  GST_FLOW_NOT_LINKED       =   -1,
  GST_FLOW_FLUSHING         =   -2,
  GST_FLOW_EOS              =   -3,
  GST_FLOW_NOT_NEGOTIATED   =   -4,
  GST_FLOW_ERROR            =   -5,
  GST_FLOW_NOT_SUPPORTED    =   -6,
  GST_FLOW_CUSTOM_ERROR     = -100,
  GST_FLOW_CUSTOM_ERROR_1   = -101,
  GST_FLOW_CUSTOM_ERROR_2   = -102
} GstFlowReturn;

const gchar *gst_flow_get_name (GstFlowReturn ret);
