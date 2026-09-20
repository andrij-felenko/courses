#include "cc1101.h"
#include <stdio.h>
#include <string.h>

// Режим вузла: ініціатор або відповідач
typedef enum {
    ROLE_PING,
    ROLE_PONG
} NodeRole;

volatile bool packetEvent = false;

// Обробник переривання від GDO0 (піднято, коли пакет прийнято або надіслано).
// Прив'язується до переривань на рівні платформи.
void GDO0_InterruptHandler(void) {
    packetEvent = true; 
}

// Затримка (імплементація платформи)
extern void Delay_ms(uint32_t ms);

int main(void) {
    // Ініціалізація платформи, SPI, пінів, переривань
    // Platform_Init();
    
    CC1101_Init();
    
    NodeRole role = ROLE_PING; // Роль поточного вузла
    CC1101_Packet pkt;
    
    if (role == ROLE_PONG) {
        CC1101_SetRx();
    }
    
    while (1) {
        if (role == ROLE_PING) {
            // Відправка повідомлення PING
            const char *msg = "PING";
            pkt.length = strlen(msg);
            memcpy(pkt.data, msg, pkt.length);
            
            CC1101_SendPacket(&pkt);
            
            // Затримка, щоб трансивер встиг відправити дані
            Delay_ms(10); 
            
            // Перемикаємось на приймання
            CC1101_SetRx();
            packetEvent = false;
            
            // Чекаємо на відповідь (спрощено, в реальності потрібен таймаут)
            while (!packetEvent);
            
            if (CC1101_ReceivePacket(&pkt)) {
                // Пакет PONG отримано
                // Обробка даних з pkt.data
            }
            
            Delay_ms(1000); // Затримка перед наступним PING
            
        } else if (role == ROLE_PONG) {
            if (packetEvent) {
                packetEvent = false;
                
                if (CC1101_ReceivePacket(&pkt)) {
                    if (strncmp((char*)pkt.data, "PING", pkt.length) == 0) {
                        // Відповідаємо PONG
                        const char *msg = "PONG";
                        pkt.length = strlen(msg);
                        memcpy(pkt.data, msg, pkt.length);
                        
                        Delay_ms(5); // Невелика затримка на підготовку
                        CC1101_SendPacket(&pkt);
                        Delay_ms(10); // Очікування завершення передавання
                        
                        CC1101_SetRx(); // Повернення до очікування
                    }
                }
            }
        }
    }
    
    return 0;
}
