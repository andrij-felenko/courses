/* core/inc/compiler_port.h */
#ifndef COMPILER_PORT_H
#define COMPILER_PORT_H

#include <stdint.h>
#include <stddef.h>

#if defined(__GNUC__) || defined(__clang__)
    /* GCC та Clang розширення */
    #define PORT_RAMFUNC        __attribute__((section(".ramfunc"), noinline))
    #define PORT_NORETURN       __attribute__((noreturn))
    #define PORT_ALIGNED(n)     __attribute__((aligned(n)))
    #define PORT_PACKED_STRUCT  struct __attribute__((packed))
    #define PORT_WEAK           __attribute__((weak))
    #define PORT_NAKED          __attribute__((naked))

    #define PORT_BARRIER()      __asm volatile("" ::: "memory")
    #define PORT_NOP()          __asm volatile("nop")

#elif defined(__ICCARM__)
    /* IAR Embedded Workbench розширення */
    #define PORT_RAMFUNC        __ramfunc
    #define PORT_NORETURN       __noreturn
    #define PORT_ALIGNED(n)     _Pragma(STRINGIFY(data_alignment=n))
    #define PORT_PACKED_STRUCT  __packed struct
    #define PORT_WEAK           __weak
    #define PORT_NAKED          __stackless

    #define PORT_BARRIER()      __asm volatile("" ::: "memory")
    #define PORT_NOP()          __no_operation()

#elif defined(__CC_ARM)
    /* Keil Arm Compiler 5 (ArmCC застарілий) */
    #define PORT_RAMFUNC        __attribute__((section("ram_functions")))
    #define PORT_NORETURN       __declspec(noreturn)
    #define PORT_ALIGNED(n)     __align(n)
    #define PORT_PACKED_STRUCT  __packed struct
    #define PORT_WEAK           __weak
    #define PORT_NAKED          __asm

    #define PORT_BARRIER()      __schedule_barrier()
    #define PORT_NOP()          __nop()
#else
    #error "Невідомий компілятор: додайте відповідні макроси розширень"
#endif

/* Приклад використання у C */
PORT_PACKED_STRUCT TelemetryFrame {
    uint32_t timestamp_ms;
    uint16_t voltage_mv;
    uint16_t current_ma;
    uint8_t  status_flags;
};

PORT_RAMFUNC void flash_critical_write_page(uint32_t page_addr, const uint8_t *data, size_t len);

#endif /* COMPILER_PORT_H */
