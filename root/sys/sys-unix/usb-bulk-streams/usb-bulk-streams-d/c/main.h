struct usb_host_endpoint *eps[3] = { ep_status, ep_in, ep_out };
int n;

n = usb_alloc_streams(intf, eps, 3, MAX_TAGS, GFP_NOIO);
if (n < 2)
        return work_without_streams(dev);   /* одна команда за раз */

/* кожна команда бере свій тег і кладе заявку у СВОЄ кільце */
urb->stream_id = tag;                       /* 1 … n */
usb_submit_urb(urb, GFP_NOIO);
