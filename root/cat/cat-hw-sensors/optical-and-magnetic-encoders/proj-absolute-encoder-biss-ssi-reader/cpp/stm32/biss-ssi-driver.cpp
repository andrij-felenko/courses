#include "stm32f4xx_hal.h"

class BiSS_SSI_Driver {
private:
    SPI_HandleTypeDef* hspi_;
    uint8_t rx_buffer_[3];
public:
    BiSS_SSI_Driver(SPI_HandleTypeDef* hspi) : hspi_(hspi) {}

    bool readFrame(uint32_t& raw_position, uint8_t& status_flags) {
        if (HAL_SPI_Receive(hspi_, rx_buffer_, sizeof(rx_buffer_), 10) != HAL_OK) {
            return false;
        }
        raw_position = ((uint32_t)rx_buffer_[0] << 16) | 
                       ((uint32_t)rx_buffer_[1] << 8)  | 
                       rx_buffer_[2];
        status_flags = rx_buffer_[2] & 0x0F;
        return true;
    }
};
