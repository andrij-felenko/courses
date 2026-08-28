/* Фрагмент логіки ядра: net/core/dev.c */
int dev_alloc_name(struct net_device *dev, const char *name)
{
    char buf[IFNAMSIZ];
    struct net *net = dev_net(dev);
    int ret;

    ret = __dev_alloc_name(net, name, buf);
    if (ret >= 0)
        strscpy(dev->name, buf, IFNAMSIZ);
    return ret;
}
