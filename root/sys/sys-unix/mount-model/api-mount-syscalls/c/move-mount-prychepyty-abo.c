int fsfd = sys_fsopen("tmpfs", FSOPEN_CLOEXEC);
if (fsfd < 0) return -1;

sys_fsconfig(fsfd, FSCONFIG_SET_STRING, "size", "64m", 0);
sys_fsconfig(fsfd, FSCONFIG_SET_STRING, "mode", "0700", 0);

if (sys_fsconfig(fsfd, FSCONFIG_CMD_CREATE, NULL, NULL, 0) < 0) {
    drain_messages(fsfd);           /* тут скажуть, яка саме опція погана */
    return -1;
}

int mfd = sys_fsmount(fsfd, FSMOUNT_CLOEXEC,
                      MOUNT_ATTR_NOSUID | MOUNT_ATTR_NODEV);
close(fsfd);                        /* контекст більше не потрібен */

/* до цієї миті монтування існує, але шляху до нього немає */
sys_move_mount(mfd, "", AT_FDCWD, "/mnt/scratch",
               MOVE_MOUNT_F_EMPTY_PATH);
close(mfd);
