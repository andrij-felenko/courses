/* ✗ подвійне звільнення: push_event уже забрав подію */
gst_pad_push_event (pad, event);
gst_event_unref (event);

/* ✗ витік: обробник з'їв подію, але не звільнив її */
case GST_EVENT_CUSTOM_DOWNSTREAM:
  my_handle (event);
  return TRUE;             /* треба gst_event_unref (event) перед цим */

/* ✓ переслати ту саму подію двом падам — по посиланню на кожен */
gst_pad_push_event (pad_a, gst_event_ref (event));
gst_pad_push_event (pad_b, event);
