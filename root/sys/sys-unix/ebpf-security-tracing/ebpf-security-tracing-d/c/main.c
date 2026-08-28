SEC("kprobe/commit_creds")
int BPF_KPROBE(trace_commit_creds, struct cred *new_cred)
{
    u32 old_uid = (u32)bpf_get_current_uid_gid();
    u32 new_uid = BPF_CORE_READ(new_cred, uid.val);

    // Виявлення переходу з непривілейованого користувача у root
    if (old_uid != 0 && new_uid == 0) {
        // Формування тривожної події безпеки
    }
    return 0;
}
