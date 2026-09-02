#include <cstring>

#include "eth_driver.hpp"

extern "C" {
#include "lwip/opt.h"
#include "lwip/sys.h"
#include "netif/etharp.h"
}

namespace {

constexpr char kIfName0 = 'e';
constexpr char kIfName1 = 'n';
constexpr int kThreadStack = 1024;
constexpr int kThreadPrio = TCPIP_THREAD_PRIO + 1;

/// Та сама адреса, що записана в MACA0HR/MACA0LR під час ініціалізації MAC.
constexpr std::uint8_t kMacAddr[ETH_HWADDR_LEN] = {0x02, 0x00, 0x00, 0x11, 0x22, 0x33};

sys_sem_t g_rxReady;

/// Вихід кадру зі стека просто в кільце DMA — без проміжного буфера.
err_t lowLevelOutput(struct netif* netif, struct pbuf* p)
{
    LWIP_UNUSED_ARG(netif);

    const auto sent = net::mac().send(p);
    if (sent) {
        return ERR_OK;
    }
    switch (sent.error()) {
        case net::TxError::RingFull:
            // «Спробуй пізніше»: TCP перешле сегмент сам, датаграма UDP згине.
            return ERR_MEM;
        case net::TxError::TooManySegments:
        case net::TxError::SegmentTooLong:
            // Кадр із такою кількістю ланок кільце не вміщує в принципі.
            return ERR_BUF;
        case net::TxError::EmptyFrame:
            return ERR_ARG;
    }
    return ERR_IF;
}

/// Окрема задача: тут можна виділяти й звільняти pbuf, тут же живе netif->input.
void inputThread(void* arg)
{
    auto* netif = static_cast<struct netif*>(arg);

    for (;;) {
        // Таймаут навмисний: якщо сигнал переривання загубився (наприклад,
        // кільце звільнилося в момент RBUS), кадри все одно розгребуться.
        static_cast<void>(sys_arch_sem_wait(&g_rxReady, 100));

        while (net::PbufRef frame = net::mac().receive()) {
            // Володіння переходить стеку — рівно на час виклику.
            pbuf* raw = frame.release();
            if (netif->input(raw, netif) != ERR_OK) {
                pbuf_free(raw);  // стек кадр не взяв
            }
        }

        // Заразом віддаємо в пул те, що вже пішло в кабель: за одностороннього
        // трафіку наступного send можна чекати довго.
        net::mac().reclaimSent();
    }
}

}  // namespace

extern "C" err_t ethernetif_init(struct netif* netif)
{
    LWIP_ASSERT("netif != NULL", netif != nullptr);

#if LWIP_NETIF_HOSTNAME
    netif->hostname = "lwip-zc";
#endif
    netif->name[0] = kIfName0;
    netif->name[1] = kIfName1;
    netif->output = etharp_output;
    netif->linkoutput = lowLevelOutput;
    netif->mtu = 1500;
    netif->hwaddr_len = ETH_HWADDR_LEN;
    std::memcpy(netif->hwaddr, kMacAddr, ETH_HWADDR_LEN);
    netif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_LINK_UP;

    if (sys_sem_new(&g_rxReady, 0) != ERR_OK) {
        return ERR_MEM;
    }

    // Порядок важливий: семафор мусить існувати раніше, ніж дозволено
    // переривання ETH, — інакше перший же кадр сигналить у порожнечу.
    if (!net::mac().init()) {
        sys_sem_free(&g_rxReady);
        return ERR_MEM;
    }

    sys_thread_new("ethif", inputThread, netif, kThreadStack, kThreadPrio);
    return ERR_OK;
}

extern "C" void ETH_IRQHandler(void)
{
    net::mac().serviceIrq();
}

extern "C" void ethernetif_notify_from_isr(void)
{
    // Порт lwIP мусить мати ISR-безпечний sys_sem_signal (у FreeRTOS-порті це
    // xSemaphoreGiveFromISR). Нічого важчого з переривання ми не робимо.
    sys_sem_signal(&g_rxReady);
}
