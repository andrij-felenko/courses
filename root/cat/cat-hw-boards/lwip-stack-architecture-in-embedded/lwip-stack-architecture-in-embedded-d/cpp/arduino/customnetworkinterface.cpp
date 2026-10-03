#include <lwip/netif.h>
#include <lwip/pbuf.h>
#include <netif/etharp.h>
#include <lwip/tcpip.h>

class CustomNetworkInterface {
private:
    netif _netif;
    uint8_t _mac[6];

    static err_t linkoutput_cpp(netif* nif, pbuf* p) {
        auto* self = static_cast<CustomNetworkInterface*>(nif->state);
        return self->handleTx(p);
    }

    err_t handleTx(pbuf* p) {
        for (pbuf* q = p; q != nullptr; q = q->next) {
            // Передача фрагмента q->payload довжиною q->len в SPI/UART або Ethernet MAC
        }
        return ERR_OK;
    }

public:
    CustomNetworkInterface() {
        memset(&_netif, 0, sizeof(_netif));
    }

    bool begin(const uint8_t mac[6], ip4_addr_t ip, ip4_addr_t netmask, ip4_addr_t gw) {
        memcpy(_mac, mac, 6);
        _netif.state = this;

        if (!netif_add(&_netif, &ip, &netmask, &gw, this, initCallback, tcpip_input)) {
            return false;
        }

        netif_set_default(&_netif);
        netif_set_up(&_netif);
        netif_set_link_up(&_netif);
        return true;
    }

    static err_t initCallback(netif* nif) {
        auto* self = static_cast<CustomNetworkInterface*>(nif->state);
        nif->name[0] = 'w';
        nif->name[1] = 'n';
        nif->output = etharp_output;
        nif->linkoutput = linkoutput_cpp;
        nif->mtu = 1500;
        nif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_LINK_UP;
        nif->hwaddr_len = 6;
        memcpy(nif->hwaddr, self->_mac, 6);
        return ERR_OK;
    }

    void onPacketReceived(uint8_t* data, uint16_t len) {
        pbuf* p = pbuf_alloc(PBUF_RAW, len, PBUF_POOL);
        if (p) {
            pbuf_take(p, data, len);
            if (_netif.input(p, &_netif) != ERR_OK) {
                pbuf_free(p);
            }
        }
    }
};
