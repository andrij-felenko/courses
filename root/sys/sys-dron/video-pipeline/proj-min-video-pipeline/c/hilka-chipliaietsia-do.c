static gboolean link_to_tee(App *a, GstElement *branch, GstPad **keep)
{
    GstPad *tee_pad = gst_element_request_pad_simple(a->tee, "src_%u");
    GstPad *in      = gst_element_get_static_pad(branch, "sink");

    const GstPadLinkReturn ret = gst_pad_link(tee_pad, in);
    gst_object_unref(in);                 /* get_static_pad віддає посилання */

    if (ret != GST_PAD_LINK_OK) {
        gst_element_release_request_pad(a->tee, tee_pad);
        gst_object_unref(tee_pad);
        return FALSE;
    }
    if (keep) *keep = tee_pad;            /* пад лишається на нас */
    else      gst_object_unref(tee_pad);
    return TRUE;
}
