static void status_done(struct urb *urb)
{
        struct dev_state *d = urb->context;   /* заявка належить кільцю, не команді */
        unsigned long flags;
        struct cmd *c;
        unsigned int t;

        switch (urb->status) {
        case 0:
                break;
        case -ENOENT:            /* usb_kill_urb */
        case -ECONNRESET:        /* usb_unlink_urb */
        case -ESHUTDOWN:         /* точка вимкнена або пристрій зник */
                return;          /* прибирає той, хто скасовував */
        case -EPIPE:             /* STALL: стала вся точка, не один стрим */
                schedule_work(&d->halt_work);
                return;
        default:
                goto requeue;
        }

        t = urb->stream_id - 1;
        spin_lock_irqsave(&d->lock, flags);
        c = (t < d->n_tags && test_bit(t, d->tag_map)) ? d->cmds[t] : NULL;
        spin_unlock_irqrestore(&d->lock, flags);

        if (!c) {
                dev_warn(&d->intf->dev, "статус на чужому стримі %u\n", urb->stream_id);
                goto requeue;
        }

        if (atomic_dec_and_test(&c->parts))
                finish_cmd(c);   /* дані й статус прийшли обоє */

requeue:
        if (!READ_ONCE(d->quiescing))
                usb_submit_urb(urb, GFP_ATOMIC);   /* кільце знову слухає */
}
