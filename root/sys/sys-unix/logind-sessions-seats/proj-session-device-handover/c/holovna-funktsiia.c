#define TRY(expr, what) do { int _r = (expr); if (_r < 0) {                 \
        fprintf(stderr, "%s: %s\n", (what), strerror(-_r)); return 1; } } while (0)

int main(int argc, char **argv) {
    Ctx c = { .fd = -1 };
    const char *node = argc > 1 ? argv[1] : "/dev/input/event0";
    sd_bus_message *reply = NULL;
    char *session = NULL;
    const char *path;
    struct stat st;
    int devfd, inactive;

    /* 1. котрий сеанс наш: читається з cgroup процесу, шину не питаємо */
    TRY(sd_pid_get_session(0, &session), "не в сеансі logind");

    TRY(sd_event_default(&c.event), "sd_event_default");
    TRY(sd_bus_open_system(&c.bus), "sd_bus_open_system");   /* ВЛАСНЕ з'єднання */
    TRY(sd_bus_attach_event(c.bus, c.event, 0), "sd_bus_attach_event");

    /* 2. об'єктний шлях сеансу — саме він, а не /session/self */
    TRY(sd_bus_call_method(c.bus, LOGIND, MGR_PATH, MGR_IFACE, "GetSession",
                           NULL, &reply, "s", session), "GetSession");
    TRY(sd_bus_message_read(reply, "o", &path), "read path");
    c.path = strdup(path);
    sd_bus_message_unref(reply);

    /* 3. підписка ДО TakeDevice, інакше перша ж пауза пролетить повз */
    TRY(sd_bus_match_signal(c.bus, NULL, LOGIND, c.path, SES_IFACE,
                            "PauseDevice", on_pause, &c), "match PauseDevice");
    TRY(sd_bus_match_signal(c.bus, NULL, LOGIND, c.path, SES_IFACE,
                            "ResumeDevice", on_resume, &c), "match ResumeDevice");

    /* 4. розпорядник сеансу; force=false — інакше треба бути root */
    TRY(sd_bus_call_method(c.bus, LOGIND, c.path, SES_IFACE, "TakeControl",
                           NULL, NULL, "b", 0), "TakeControl");

    /* 5. номери пристрою беремо з самого вузла */
    if (stat(node, &st) < 0) { perror(node); return 1; }
    c.major = major(st.st_rdev);
    c.minor = minor(st.st_rdev);

    /* 6. пристрій приходить уже відкритим */
    TRY(sd_bus_call_method(c.bus, LOGIND, c.path, SES_IFACE, "TakeDevice",
                           NULL, &reply, "uu", c.major, c.minor), "TakeDevice");
    TRY(sd_bus_message_read(reply, "hb", &devfd, &inactive), "read fd");
    c.fd = fcntl(devfd, F_DUPFD_CLOEXEC, 3);
    sd_bus_message_unref(reply);
    if (c.fd < 0) { perror("dup"); return 1; }
    fcntl(c.fd, F_SETFL, O_NONBLOCK);

    if (inactive)
        printf("сеанс неактивний: дескриптор мертвий, чекаємо на ResumeDevice\n");
    else
        TRY(arm(&c), "sd_event_add_io");

    TRY(sd_event_loop(c.event), "sd_event_loop");

    sd_bus_call_method(c.bus, LOGIND, c.path, SES_IFACE, "ReleaseDevice",
                       NULL, NULL, "uu", c.major, c.minor);
    sd_bus_call_method(c.bus, LOGIND, c.path, SES_IFACE, "ReleaseControl",
                       NULL, NULL, NULL);
    return 0;
}
