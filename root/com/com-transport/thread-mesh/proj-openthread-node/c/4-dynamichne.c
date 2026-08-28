static void handle_joiner_callback(otError error, void *context)
{
    if (error == OT_ERROR_NONE) {
        printf("[Joiner] Комісіонування успішне! Запуск Thread...\n");
        otThreadSetEnabled((otInstance *)context, true);
    } else {
        printf("[Joiner Помилка] Код: %d\n", error);
    }
}

void start_secure_commissioning(otInstance *instance, const char *pskd)
{
    /* Запуск DTLS-рукостискання ECJPAKE через найближчий Joiner Router */
    otJoinerStart(instance, pskd, NULL, "VendorLab", "TempSensor", "v1.0", NULL, 
                  handle_joiner_callback, instance);
}
