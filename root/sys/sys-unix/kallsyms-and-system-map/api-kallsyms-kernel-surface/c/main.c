/* Концептуальна логіка перевірки kptr_restrict у ядрі Linux */
static bool kallsyms_show_value(const struct cred *cred)
{
    switch (kptr_restrict) {
    case 0:
        return true;
    case 1:
        if (has_ns_capability(cred, &init_user_ns, CAP_SYSLOG))
            return true;
        fallthrough;
    case 2:
    default:
        return false;
    }
}
