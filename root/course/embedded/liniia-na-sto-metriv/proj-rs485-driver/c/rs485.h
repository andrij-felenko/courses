/* rs485.h — напівдуплексний драйвер RS-485.
 *
 * Драйвер веде автомат кадру: вмикає DE перед першим байтом, знімає його
 * СТРОГО за подією TC, звіряє власне відлуння з переданим байтом і міряє
 * паузи тиші T1.5 / T3.5 за Modbus RTU.
 *
 * Про регістри драйвер не знає нічого: усе, що торкається периферії, лежить
 * у хуках rs485_hw_t (реалізація для STM32 — у stm32_port.c).
 */
#ifndef RS485_H
#define RS485_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define RS485_BUF_SIZE 256u

/* Прапорці помилок приймача, зняті зі статусного регістра UART */
#define RS485_RX_OVERRUN 0x01u
#define RS485_RX_FRAMING 0x02u
#define RS485_RX_NOISE   0x04u

typedef enum {
    RS485_OK = 0,
    RS485_ERR_BUSY,       /* шина зайнята або ще триває пауза розвороту */
    RS485_ERR_TOO_LONG,   /* кадр не вміщається в буфер */
    RS485_ERR_COLLISION,  /* відлуння не збіглося з переданим байтом */
    RS485_ERR_NO_ECHO,    /* байти пішли, а відлуння не повернулося: обрив або КЗ */
    RS485_ERR_GAP,        /* пауза всередині кадру перевищила T1.5 */
    RS485_ERR_OVERRUN,
    RS485_ERR_FRAMING,
    RS485_ERR_NOISE
} rs485_err_t;

typedef enum {
    RS485_IDLE = 0,   /* шина вільна, можна передавати */
    RS485_RX,         /* збираємо кадр, чекаємо тиші T3.5 */
    RS485_TX,         /* DMA виштовхує байти в TDR */
    RS485_TX_DRAIN,   /* DMA скінчив, чекаємо TC — DE ще піднято */
    RS485_GUARD       /* пауза розвороту після власного передавання */
} rs485_state_t;

/* Для чого саме зараз заряджено таймер пауз */
typedef enum {
    RS485_T_NONE = 0,
    RS485_T_T15,      /* міжсимвольний інтервал */
    RS485_T_T35,      /* решта тиші до кінця кадру */
    RS485_T_GUARD     /* захисна пауза після власного кадру */
} rs485_timer_job_t;

typedef struct {
    /* NULL, якщо DE веде сама периферія (USART_CR3_DEM) */
    void (*set_de)(bool on);
    void (*tx_dma_start)(const uint8_t *buf, size_t len);
    void (*tx_dma_abort)(void);
    void (*tc_irq_enable)(bool on);
    void (*rx_error_clear)(void);
    void (*timer_arm_us)(uint32_t us);
    void (*timer_stop)(void);
    /* Критична секція: стан автомата читають і пишуть переривання */
    uint32_t (*irq_lock)(void);
    void (*irq_unlock)(uint32_t saved);
} rs485_hw_t;

typedef struct {
    uint32_t frames;      /* прийнято цілих кадрів */
    uint32_t gaps;        /* кадрів зіпсовано міжсимвольною паузою */
    uint32_t collisions;  /* розбіжностей відлуння */
    uint32_t overruns;
    uint32_t framings;
    uint32_t noises;
    uint32_t no_echo;
} rs485_stats_t;

typedef struct {
    rs485_hw_t hw;
    uint32_t t15_us;
    uint32_t t35_us;

    uint8_t tx_buf[RS485_BUF_SIZE];
    size_t  tx_len;
    volatile size_t echo_idx;   /* скільки власних байтів повернулося з лінії */
    volatile bool   echo_wait;

    uint8_t rx_buf[RS485_BUF_SIZE];
    volatile size_t rx_len;
    volatile bool   rx_discard; /* попередній кадр ще не забрали — цей губимо */
    volatile bool   frame_bad;  /* у кадрі був збій, віддавати не можна */
    volatile bool   frame_ready;

    volatile rs485_state_t     state;
    volatile rs485_timer_job_t timer_job;
    volatile rs485_err_t       last_error;
    rs485_stats_t stats;
} rs485_port_t;

void        rs485_init(rs485_port_t *p, const rs485_hw_t *hw, uint32_t baud);
rs485_err_t rs485_send(rs485_port_t *p, const uint8_t *data, size_t len);

bool           rs485_frame_ready(const rs485_port_t *p);
const uint8_t *rs485_frame(const rs485_port_t *p, size_t *len);
void           rs485_frame_release(rs485_port_t *p);
rs485_err_t    rs485_take_error(rs485_port_t *p);
const rs485_stats_t *rs485_stats(const rs485_port_t *p);

/* Точки входу з переривань */
void rs485_isr_rx(rs485_port_t *p, uint8_t byte);
void rs485_isr_rx_error(rs485_port_t *p, uint32_t flags);
void rs485_isr_dma_done(rs485_port_t *p);
void rs485_isr_uart_tc(rs485_port_t *p);
void rs485_isr_timer(rs485_port_t *p);

/* Порт плати (stm32_port.c) */
void          rs485_board_init(uint32_t baud);
rs485_port_t *rs485_bus(void);

#endif /* RS485_H */
