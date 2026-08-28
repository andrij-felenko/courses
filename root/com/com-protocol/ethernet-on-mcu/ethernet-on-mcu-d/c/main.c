#include "esp_eth.h"
#include "esp_netif.h"
#include "esp_event.h"

// Викликається, коли DHCP видав адресу — мережа готова до сокетів
static void on_got_ip(void *arg, esp_event_base_t base,
                      int32_t id, void *data) {
    ip_event_got_ip_t *e = (ip_event_got_ip_t *)data;
    printf("Ethernet піднявся, IP: " IPSTR "\n", IP2STR(&e->ip_info.ip));
    // ── ТУТ далі — той самий socket()/connect()/send(), що й по Wi-Fi ──
}

void ethernet_start(void) {
    // 1. Базова інфраструктура мережі та подій
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_config_t netif_cfg = ESP_NETIF_DEFAULT_ETH();
    esp_netif_t *eth_netif = esp_netif_new(&netif_cfg);

    // 2. MAC — він у самому ESP32; задаємо ніжки керування PHY (MDC/MDIO)
    eth_mac_config_t mac_cfg = ETH_MAC_DEFAULT_CONFIG();
    eth_esp32_emac_config_t emac_cfg = ETH_ESP32_EMAC_DEFAULT_CONFIG();
    emac_cfg.smi_gpio.mdc_num  = 23;
    emac_cfg.smi_gpio.mdio_num = 18;
    esp_eth_mac_t *mac = esp_eth_mac_new_esp32(&emac_cfg, &mac_cfg);

    // 3. PHY — зовнішній чип (тут LAN87xx); скидання через окрему ніжку
    eth_phy_config_t phy_cfg = ETH_PHY_DEFAULT_CONFIG();
    phy_cfg.phy_addr       = 1;
    phy_cfg.reset_gpio_num = 5;
    esp_eth_phy_t *phy = esp_eth_phy_new_lan87xx(&phy_cfg);

    // 4. Зводимо MAC+PHY у драйвер і чіпляємо його до мережевого стеку
    esp_eth_config_t eth_cfg = ETH_DEFAULT_CONFIG(mac, phy);
    esp_eth_handle_t eth = NULL;
    esp_eth_driver_install(&eth_cfg, &eth);
    esp_netif_attach(eth_netif, esp_eth_new_netif_glue(eth));

    // 5. Ловимо подію «отримано IP» і запускаємо Ethernet
    esp_event_handler_register(IP_EVENT, IP_EVENT_ETH_GOT_IP,
                               &on_got_ip, NULL);
    esp_eth_start(eth);   // піднімає лінк; esp_netif сам веде DHCP-клієнт
}
