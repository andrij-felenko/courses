DEFINE_WAIT(wait);
int ret = 0;

for (;;) {
    prepare_to_wait(&dev->readq, &wait, TASK_INTERRUPTIBLE);
    if (READ_ONCE(dev->bytes_ready))
        break;
    if (signal_pending(current)) { ret = -ERESTARTSYS; break; }
    submit_next_request(dev);       /* власна дія перед сном */
    schedule();
}
finish_wait(&dev->readq, &wait);
return ret;
