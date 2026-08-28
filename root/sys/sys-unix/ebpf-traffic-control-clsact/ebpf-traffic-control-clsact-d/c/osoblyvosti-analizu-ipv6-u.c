#include <linux/ipv6.h>

struct ipv6hdr *ip6 = (void *)(eth + 1);
if ((void *)(ip6 + 1) > data_end) {
    return TC_ACT_OK;
}

__u8 next_hdr = ip6->nexthdr;
void *hdr_ptr = (void *)(ip6 + 1);

// Цикл із фіксованою кількістю ітерацій для верифікатора
#pragma unroll
for (int i = 0; i < 4; i++) {
    if (next_hdr == IPPROTO_TCP) {
        break; // Знайшли TCP заголовок
    }
    
    struct ipv6_opt_hdr *ext_hdr = hdr_ptr;
    if ((void *)(ext_hdr + 1) > data_end) {
        return TC_ACT_OK;
    }
    
    // Переходимо до наступного розширеного заголовка
    hdr_ptr += (ext_hdr->hdrlen + 1) * 8;
    next_hdr = ext_hdr->nexthdr;
}
