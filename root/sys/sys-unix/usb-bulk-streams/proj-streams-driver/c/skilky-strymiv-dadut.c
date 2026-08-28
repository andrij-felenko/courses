#define MAX_TAGS 32                       /* стеля цього драйвера */

struct dev_state {
        struct usb_device    *udev;
        struct usb_interface *intf;
        unsigned int cmd_pipe, status_pipe, data_in_pipe, data_out_pipe;

        bool         use_streams;
        unsigned int n_tags;              /* скільки тегів дозволено вживати */
        bool         quiescing;

        spinlock_t   lock;
        DECLARE_BITMAP(tag_map, MAX_TAGS);
        struct cmd  *cmds[MAX_TAGS];
        struct urb  *status_urb[MAX_TAGS];
        struct work_struct halt_work;
};

static void setup_streams(struct dev_state *d,
                          struct usb_host_endpoint *status_ep,
                          struct usb_host_endpoint *in_ep,
                          struct usb_host_endpoint *out_ep)
{
        struct usb_host_endpoint *eps[3] = { status_ep, in_ep, out_ep };
        int n;

        /* на USB 2 номер стриму нікуди записати: у заголовку немає поля */
        if (d->udev->speed < USB_SPEED_SUPER)
                goto no_streams;

        n = usb_alloc_streams(d->intf, eps, ARRAY_SIZE(eps), MAX_TAGS, GFP_NOIO);
        if (n < 2) {
                /* XHCI_BROKEN_STREAMS, дешевий міст, брак пам'яті — усе сюди */
                dev_info(&d->intf->dev, "стримів немає (%d), одна команда за раз\n", n);
                goto no_streams;
        }

        d->use_streams = true;
        d->n_tags = n;            /* менше, ніж просили, — норма; більше не буває */
        return;

no_streams:
        d->use_streams = false;
        d->n_tags = 1;            /* це НЕ помилка probe: драйвер працює далі */
}
