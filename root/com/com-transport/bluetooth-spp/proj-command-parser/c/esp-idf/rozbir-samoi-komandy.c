static void handle_command(const char *cmd)
{
    int  value;
    char msg[80];

    if      (strcmp(cmd, "LED ON")  == 0) gpio_set_level(LED_GPIO, 1);
    else if (strcmp(cmd, "LED OFF") == 0) gpio_set_level(LED_GPIO, 0);
    else if (strcmp(cmd, "STOP")    == 0) set_speed(0);
    else if (sscanf(cmd, "SPEED %d", &value) == 1) set_speed(value);   // "SPEED 120" → value=120
    else {
        int n = snprintf(msg, sizeof(msg), "? невідома команда: %s\n", cmd);
        esp_spp_write(spp_handle, n, (uint8_t *) msg);   // відповідь у той самий потік
    }

    esp_spp_write(spp_handle, 3, (uint8_t *) "OK\n");    // підтвердження — зворотний зв'язок
}
