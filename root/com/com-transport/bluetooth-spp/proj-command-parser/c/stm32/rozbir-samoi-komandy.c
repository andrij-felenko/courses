static void HandleCommand(const char *cmd)
{
    int  value;
    char msg[80];

    if      (strcmp(cmd, "LED ON")  == 0) HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
    else if (strcmp(cmd, "LED OFF") == 0) HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
    else if (strcmp(cmd, "STOP")    == 0) SetSpeed(0);
    else if (sscanf(cmd, "SPEED %d", &value) == 1) SetSpeed(value);    // "SPEED 120" → value=120
    else {
        int n = snprintf(msg, sizeof(msg), "? невідома команда: %s\r\n", cmd);
        HAL_UART_Transmit(&huart1, (uint8_t *) msg, n, 100);   // відповідь у той самий потік
    }

    HAL_UART_Transmit(&huart1, (uint8_t *) "OK\r\n", 4, 100);  // підтвердження — зворотний зв'язок
}
