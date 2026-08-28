void SVC_Handler_C(uint32_t *svc_args) {
    /* svc_args[6] містить PC повернення */
    uint8_t svc_number = ((uint8_t *)svc_args[6])[-2];
    uint32_t param0    = svc_args[0];
    uint32_t param1    = svc_args[1];

    switch (svc_number) {
        case 0x01: /* SYS_YIELD */
            SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk;
            svc_args[0] = 0;
            break;
        case 0x02: /* SYS_UART_WRITE (param0 = buf, param1 = len) */
            if (mpu_validate_buffer((const void*)param0, (size_t)param1, false)) {
                /* Буфер валідний, виконання передачі */
                svc_args[0] = uart_transmit_blocking((const uint8_t*)param0, param1);
            } else {
                svc_args[0] = (uint32_t)-13; /* -EACCES */
            }
            break;
        default:
            svc_args[0] = (uint32_t)-38; /* -ENOSYS */
            break;
    }
}
