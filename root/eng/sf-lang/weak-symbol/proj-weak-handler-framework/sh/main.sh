# До лінкування в об'єктних файлах:
nm hal_driver_core.o | grep callback
0000000000000000 W hal_uart_rx_callback
0000000000000000 W hal_spi_transfer_callback

nm app_main.o | grep callback
0000000000000000 T hal_uart_rx_callback

# Після лінкування у фінальному ELF:
nm test_harness.elf | grep callback
0000000000401300 T hal_uart_rx_callback      # Сильний символ переміг!
00000000004011e0 W hal_spi_transfer_callback   # Слабкий аліас на stub
