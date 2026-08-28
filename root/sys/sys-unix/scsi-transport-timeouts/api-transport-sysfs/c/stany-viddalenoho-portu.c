enum fc_port_state {
    FC_PORTSTATE_UNKNOWN,     /* Стан не визначено (початкова ініціалізація) */
    FC_PORTSTATE_NOTPRESENT,  /* Порт відсутній у таблиці фабрики */
    FC_PORTSTATE_ONLINE,      /* Нормальна робота: порт доступний, I/O виконується */
    FC_PORTSTATE_BLOCKED,     /* Зв'язок обірвано: черги заблоковано, очікування відновлення */
    FC_PORTSTATE_BYPASS,      /* Порт тимчасово виведено з топології (FC-AL bypass) */
    FC_PORTSTATE_DIAGNOSTICS, /* Виконуються діагностичні тести адаптера */
    FC_PORTSTATE_LINKDOWN,    /* Низькорівневий обрив оптичного лінку на боці HBA */
    FC_PORTSTATE_ERROR,       /* Непоправна апаратна помилка порту */
    FC_PORTSTATE_UNBOUND,     /* Порт виявлено, але прив'язку до SCSI target ще не завершено */
    FC_PORTSTATE_DELETED,     /* Сплив dev_loss_tmo: пристрій вилучається з системи */
    FC_PORTSTATE_MARGINAL,    /* Порт демонструє високий рівень бітових помилок (marginal) */
};
