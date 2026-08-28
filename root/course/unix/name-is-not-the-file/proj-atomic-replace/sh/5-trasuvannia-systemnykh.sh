bpftrace -e '
tracepoint:syscalls:sys_enter_renameat2 {
    printf("RENAME: old=%s -> new=%s, flags=%d\n", 
           str(args->oldname), str(args->newname), args->flags);
}
tracepoint:ext4:ext4_unlink_enter {
    printf("EXT4_UNLINK: parent_dir_ino=%lu, name=%s\n", 
           args->dir, str(args->dentry));
}
'
