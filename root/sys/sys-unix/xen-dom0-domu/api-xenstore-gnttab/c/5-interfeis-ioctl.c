/* Прив'язка до незв'язаного порту Event Channel.
   Номер виділеного локального порту повертає сам ioctl своїм значенням —
   окремого вихідного поля в структурі немає. */
struct ioctl_evtchn_bind_unbound_port {
    unsigned int remote_domain; /* ID домену, якому дозволено з'єднатися */
};

/* Надсилання сповіщення у порт (генерація upcall) */
struct ioctl_evtchn_notify {
    unsigned int port;          /* Локальний порт для генерації upcall */
};

#define IOCTL_EVTCHN_BIND_UNBOUND_PORT \
    _IOC(_IOC_NONE, 'E', 2, sizeof(struct ioctl_evtchn_bind_unbound_port))
#define IOCTL_EVTCHN_NOTIFY            \
    _IOC(_IOC_NONE, 'E', 4, sizeof(struct ioctl_evtchn_notify))
