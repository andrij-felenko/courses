int l2_sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_1588));
if (l2_sock < 0) {
    perror("socket AF_PACKET");
}

// Прив'язка до фізичного інтерфейсу через struct sockaddr_ll
struct sockaddr_ll sll;
memset(&sll, 0, sizeof(sll));
sll.sll_family = AF_PACKET;
sll.sll_ifindex = if_nametoindex("eth0");
sll.sll_protocol = htons(ETH_P_1588); // EtherType 0x88F7

if (bind(l2_sock, (struct sockaddr *)&sll, sizeof(sll)) < 0) {
    perror("bind AF_PACKET");
}
