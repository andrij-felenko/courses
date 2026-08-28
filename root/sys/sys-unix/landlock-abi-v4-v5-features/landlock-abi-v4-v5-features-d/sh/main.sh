sudo bpftrace -e '
kprobe:landlock_add_rule {
    printf("Landlock rule added by PID %d (%s)\n", pid, comm);
}
kretprobe:security_socket_bind {
    if (retval == -13) {
        printf("Landlock blocked BIND socket for PID %d (%s)\n", pid, comm);
    }
}
'
