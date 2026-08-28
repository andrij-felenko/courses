#include <systemd/sd-journal.h>

/* через старий виклик: усе значуще втоплено в реченні */
syslog(LOG_ERR, "order %s failed at payment: %s", order, strerror(errno));

/* через рідний протокол: речення — людині, значення — полями */
sd_journal_send("MESSAGE=не вдалося провести замовлення %s", order,
                "MESSAGE_ID=8daee1d3b9a04f8e9b2c1d0a77e51234",
                "PRIORITY=3",
                "ORDER_ID=%s", order,
                "ORDER_STAGE=payment",
                "ERRNO=%d", errno,
                NULL);
