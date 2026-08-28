struct sctp_event_subscribe {
    uint8_t sctp_data_io_event;          /* Заповнювати sctp_sndrcvinfo при читанні */
    uint8_t sctp_association_event;      /* Сповіщення про відкриття/закриття асоціації */
    uint8_t sctp_address_event;          /* Зміна працездатності IP-адрес піра */
    uint8_t sctp_send_failure_event;     /* Сповіщення про неможливість доставки повідомлення */
    uint8_t sctp_peer_error_event;       /* Отримано чанк ERROR від піра */
    uint8_t sctp_shutdown_event;         /* Пір ініціював процедуру SHUTDOWN */
    uint8_t sctp_partial_delivery_event; /* Переривання часткової доставки */
    uint8_t sctp_adaptation_layer_event; /* Сповіщення про рівень адаптації */
};
