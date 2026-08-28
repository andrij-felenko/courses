int fd = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI);
struct sockaddr_hci addr = {
    .hci_family = AF_BLUETOOTH,
    .hci_dev = 0, /* hci0 */
    .hci_channel = HCI_CHANNEL_RAW
};
bind(fd, (struct sockaddr *)&addr, sizeof(addr));

/* Встановлення фільтра подій HCI_EV_LE_META */
struct hci_filter flt;
hci_filter_clear(&flt);
hci_filter_set_ptype(HCI_EVENT_PKT, &flt);
hci_filter_set_event(EVT_LE_META_EVENT, &flt);
setsockopt(fd, SOL_HCI, HCI_FILTER, &flt, sizeof(flt));
