// bsp_board_rev_a.c: Реалізація для ревізії Rev A (Active-High на PB12)
bsp_status_t board_led_set(board_led_id_t led, board_led_state_t state) {
    switch (led) {
        case BOARD_LED_ID_SYSTEM_STATUS:
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, 
                (state == BOARD_LED_STATE_ON) ? GPIO_PIN_SET : GPIO_PIN_RESET);
            return BSP_STATUS_OK;
        case BOARD_LED_ID_WARNING:
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, 
                (state == BOARD_LED_STATE_ON) ? GPIO_PIN_SET : GPIO_PIN_RESET);
            return BSP_STATUS_OK;
        default:
            return BSP_STATUS_ERR_INVALID_PARAM;
    }
}
