static void halt_work_fn(struct work_struct *w)
{
        struct dev_state *d = container_of(w, struct dev_state, halt_work);
        unsigned int i;

        for (i = 0; i < d->n_tags; i++)
                usb_kill_urb(d->status_urb[i]);

        if (usb_clear_halt(d->udev, d->status_pipe)) {
                usb_queue_reset_device(d->intf);   /* глухо: скидаємо пристрій */
                return;
        }

        for (i = 0; i < d->n_tags; i++)
                usb_submit_urb(d->status_urb[i], GFP_KERNEL);
        requeue_pending(d);
}
