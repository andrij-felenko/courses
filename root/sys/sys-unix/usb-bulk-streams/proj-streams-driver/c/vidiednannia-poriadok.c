static void my_disconnect(struct usb_interface *intf)
{
        struct dev_state *d = usb_get_intfdata(intf);
        struct usb_host_endpoint *eps[3] = {
                usb_pipe_endpoint(d->udev, d->status_pipe),
                usb_pipe_endpoint(d->udev, d->data_in_pipe),
                usb_pipe_endpoint(d->udev, d->data_out_pipe),
        };
        unsigned int i;

        WRITE_ONCE(d->quiescing, true);      /* 1. закрити вхід */
        cancel_work_sync(&d->halt_work);     /* 2. дочекатися відкладеного */

        for (i = 0; i < d->n_tags; i++) {    /* 3. вигнати всіх із польоту */
                usb_kill_urb(d->status_urb[i]);
                if (d->cmds[i])
                        usb_kill_urb(d->cmds[i]->data_urb);
        }

        if (d->use_streams)                  /* 4. і лише тепер звільняти */
                usb_free_streams(intf, eps, ARRAY_SIZE(eps), GFP_NOIO);
}
