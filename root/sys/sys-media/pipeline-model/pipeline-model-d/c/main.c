/* елемент, у якого готовий кадр, віддає його вниз: */
GstFlowReturn ret = gst_pad_push (self->srcpad, buf);

/* усередині gst_pad_push, стиснуто до суті: */
GstPad *peer = GST_PAD_PEER (pad);              /* пад, до якого нас з'єднали */
return peer->chainfunc (peer, parent, buf);     /* прямий виклик сусіда */

/* а це — те, що сусід зареєстрував як свою обробку: */
static GstFlowReturn
my_filter_chain (GstPad *pad, GstObject *parent, GstBuffer *buf)
{
  MyFilter *self = MY_FILTER (parent);
  /* ... обробити buf ... */
  return gst_pad_push (self->srcpad, buf);      /* і далі, наступному */
}
