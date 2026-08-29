/* chip_regs.h — Рівень 2: регістрова карта 3-осьового MEMS-акселерометра.
 *
 * Тут і тільки тут живуть числа кремнію: адреси, маски, зсуви, очікуваний
 * ідентифікатор. Жодна функція вищих рівнів не має права писати числову
 * константу регістру в тіло алгоритму.
 */
#ifndef CHIP_REGS_H
#define CHIP_REGS_H

#include <stdint.h>

/* --- Адреси регістрів --------------------------------------------------- */
#define CHIP_REG_WHO_AM_I    0x0Fu /* заводський ID кристала, лише читання    */
#define CHIP_REG_CTRL_REG1   0x20u /* ODR, режим низького споживання, осі     */
#define CHIP_REG_CTRL_REG3   0x22u /* маршрутизація переривань на вивід INT1  */
#define CHIP_REG_CTRL_REG4   0x23u /* BDU, діапазон повної шкали, роздільність*/
#define CHIP_REG_CTRL_REG5   0x24u /* вмикання буфера FIFO                    */
#define CHIP_REG_STATUS      0x27u /* прапорці готовності та перезапису даних */
#define CHIP_REG_OUT_X_L     0x28u /* перший байт блоку X/Y/Z (6 байтів)      */
#define CHIP_REG_FIFO_CTRL   0x2Eu /* режим буфера й поріг заповнення         */
#define CHIP_REG_FIFO_SRC    0x2Fu /* стан буфера: WTM, OVRN, EMPTY, рівень   */

/* Найстарший біт адреси вмикає автоінкремент адреси всередині транзакції.
 * Без нього чип віддасть шість разів той самий регістр OUT_X_L. */
#define CHIP_ADDR_AUTOINC    0x80u

/* --- Очікуваний вміст WHO_AM_I ------------------------------------------ */
#define CHIP_WHO_AM_I_VALUE  0x33u

/* --- CTRL_REG1 ----------------------------------------------------------- */
#define CTRL1_ODR_MASK       0xF0u
#define CTRL1_ODR_SHIFT      4u
#define CTRL1_LPEN           (1u << 3) /* режим низького енергоспоживання     */
#define CTRL1_ZEN            (1u << 2)
#define CTRL1_YEN            (1u << 1)
#define CTRL1_XEN            (1u << 0)
#define CTRL1_XYZ_EN         (CTRL1_XEN | CTRL1_YEN | CTRL1_ZEN)

/* --- CTRL_REG3: маршрутизація переривань --------------------------------- */
#define CTRL3_I1_WTM         (1u << 2) /* поріг заповнення FIFO на INT1       */
#define CTRL3_I1_OVERRUN     (1u << 1) /* переповнення FIFO на INT1           */
#define CTRL3_I1_ZYXDA       (1u << 4) /* готовність нового відліку на INT1   */

/* --- CTRL_REG4 ----------------------------------------------------------- */
#define CTRL4_BDU            (1u << 7) /* Block Data Update: заморозка блоку  */
#define CTRL4_FS_MASK        0x30u     /* біти [5:4] — діапазон повної шкали  */
#define CTRL4_FS_SHIFT       4u
#define CTRL4_HR             (1u << 3) /* режим високої роздільності          */

/* --- CTRL_REG5 ----------------------------------------------------------- */
#define CTRL5_FIFO_EN        (1u << 6)

/* --- STATUS -------------------------------------------------------------- */
#define STATUS_ZYXDA         (1u << 3) /* готові нові дані по всіх трьох осях */
#define STATUS_ZYXOR         (1u << 7) /* попередній відлік не встигли забрати*/

/* --- FIFO_CTRL ----------------------------------------------------------- */
#define FIFO_CTRL_MODE_MASK  0xC0u
#define FIFO_CTRL_MODE_SHIFT 6u
#define FIFO_CTRL_WTM_MASK   0x1Fu
#define FIFO_CTRL_WTM_SHIFT  0u

/* --- FIFO_SRC ------------------------------------------------------------ */
#define FIFO_SRC_WTM         (1u << 7) /* досягнуто порогу заповнення         */
#define FIFO_SRC_OVRN        (1u << 6) /* буфер переповнено, відліки втрачено */
#define FIFO_SRC_EMPTY       (1u << 5)
#define FIFO_SRC_FSS_MASK    0x1Fu     /* скільки вибірок лежить у буфері     */

/* Глибина апаратного буфера в вибірках (по 6 байтів кожна). */
#define CHIP_FIFO_DEPTH      32u
/* Довжина одного триосьового відліку на шині. */
#define CHIP_SAMPLE_BYTES    6u

/* --- Коди вихідної частоти даних (поле ODR регістру CTRL_REG1) ----------- */
typedef enum {
    CHIP_ODR_POWER_DOWN = 0x0,
    CHIP_ODR_1_HZ       = 0x1,
    CHIP_ODR_10_HZ      = 0x2,
    CHIP_ODR_25_HZ      = 0x3,
    CHIP_ODR_50_HZ      = 0x4,
    CHIP_ODR_100_HZ     = 0x5,
    CHIP_ODR_200_HZ     = 0x6,
    CHIP_ODR_400_HZ     = 0x7
} chip_odr_t;

/* --- Діапазон повної шкали (поле FS регістру CTRL_REG4) ------------------ */
typedef enum {
    CHIP_RANGE_2G  = 0,
    CHIP_RANGE_4G  = 1,
    CHIP_RANGE_8G  = 2,
    CHIP_RANGE_16G = 3
} chip_range_t;

/* --- Режими апаратного буфера (поле FM регістру FIFO_CTRL) --------------- */
typedef enum {
    CHIP_FIFO_BYPASS          = 0, /* буфер вимкнено, лише останній відлік    */
    CHIP_FIFO_MODE            = 1, /* набирає до кінця й зупиняється          */
    CHIP_FIFO_STREAM          = 2, /* кільце: нове затирає найстаріше         */
    CHIP_FIFO_STREAM_TO_FIFO  = 3  /* кільце до події, далі — добір до кінця  */
} chip_fifo_mode_t;

/* Роздільність вихідного слова. Значення дорівнює зсуву вправо, який треба
 * зробити перед розширенням знака: 12-бітний відлік вирівняно по лівому краю
 * 16-бітного слова, тож молодші 4 біти — сміття. */
typedef enum {
    CHIP_RES_16BIT = 0,
    CHIP_RES_12BIT_LEFT_ALIGNED = 4
} chip_resolution_t;

/* Чутливість у мікро-g на молодший розряд для кожного діапазону.
 * Таблиця з даташита; єдине джерело і для float-, і для цілочисельного шляху.
 * Значення дано для вже зсунутого (правильно вирівняного) коду. */
static inline int32_t chip_sensitivity_ug(chip_range_t range)
{
    switch (range) {
    case CHIP_RANGE_2G:  return 61;  /* 0.061 мг/LSB */
    case CHIP_RANGE_4G:  return 122;
    case CHIP_RANGE_8G:  return 244;
    case CHIP_RANGE_16G: return 732;
    default:             return 61;
    }
}

/* Стандартне прискорення вільного падіння, м/с². */
#define CHIP_STANDARD_GRAVITY 9.80665f

#endif /* CHIP_REGS_H */
