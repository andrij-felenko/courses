unsigned int max_reqs = nr_events;              /* саме це піде в глобальний лічильник */
nr_events = max(nr_events, num_possible_cpus() * 4);
nr_events *= 2;

if (nr_events > (0x10000000U / sizeof(struct io_event)))   /* > 8 388 608 комірок */
        return -EINVAL;
if (!nr_events || (unsigned long)max_reqs > aio_max_nr)
        return -EAGAIN;

nr_events += 2;   /* у aio_setup_ring: компенсація за комірку перекриття head/tail */
