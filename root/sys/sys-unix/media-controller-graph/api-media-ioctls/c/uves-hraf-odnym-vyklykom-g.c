struct media_v2_topology topo;
struct media_v2_entity *ents; struct media_v2_interface *intfs;
struct media_v2_pad *pads;    struct media_v2_link *links;

retry:
        memset(&topo, 0, sizeof(topo));
        if (ioctl(fd, MEDIA_IOC_G_TOPOLOGY, &topo) < 0)   /* лише лічильники */
                return -1;

        ents  = calloc(topo.num_entities,   sizeof(*ents));
        intfs = calloc(topo.num_interfaces, sizeof(*intfs));
        pads  = calloc(topo.num_pads,       sizeof(*pads));
        links = calloc(topo.num_links,      sizeof(*links));

        topo.ptr_entities   = (__u64)(uintptr_t)ents;
        topo.ptr_interfaces = (__u64)(uintptr_t)intfs;
        topo.ptr_pads       = (__u64)(uintptr_t)pads;
        topo.ptr_links      = (__u64)(uintptr_t)links;

        if (ioctl(fd, MEDIA_IOC_G_TOPOLOGY, &topo) < 0) {
                free(ents); free(intfs); free(pads); free(links);
                if (errno == ENOSPC)      /* граф змінився між проходами */
                        goto retry;
                return -1;
        }
