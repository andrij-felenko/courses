# Скільки часу kernfs_remove() чекає на спорожнення вузла
sudo bpftrace -e '
kprobe:kernfs_remove {
    @start[tid] = nsecs;
    printf("DRAIN INITIATED: kn=%p\n", arg0);
}
kretprobe:kernfs_remove /@start[tid]/ {
    printf("DRAIN COMPLETED: %d us\n", (nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}
'
