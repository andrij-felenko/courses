/* chip_regs.h — регістрова карта еталонного акселерометра.
 *
 * Тестам цей файл потрібен не менше, ніж драйверу: мок віддає байти саме
 * за цими адресами, а перевірки читають з журналу запису ті самі маски.
 * Один спільний заголовок гарантує, що тест і драйвер не розійдуться в
 * розумінні заліза — інакше зелений тест нічого не доводить.
 */
#ifndef CHIP_REGS_H
#define CHIP_REGS_H

#include <stdint.h>

/* --- Адреси регістрів ---------------------------------------------------- */
#define CHIP_REG_WHO_AM_I   0x0Fu /* заводський ідентифікатор, лише читання  */
#define CHIP_REG_CTRL1      0x20u /* ODR, режим споживання, дозвіл осей      */
#define CHIP_REG_CTRL4      0x23u /* BDU, діапазон повної шкали, роздільність*/
#define CHIP_REG_STATUS     0x27u /* прапорці готовності й перезапису даних  */
#define CHIP_REG_OUT_X_L    0x28u /* перший байт блоку X/Y/Z (шість байтів)  */
#define CHIP_REG_OUT_Z_H    0x2Du /* останній байт того самого блоку         */

/* Старший біт адреси просить чип збільшувати адресу після кожного байта.
 * Без нього пакетне читання шість разів віддасть той самий OUT_X_L — мок
 * відтворює цю пастку буквально, тому забутий біт валить тест. */
#define CHIP_REG_AUTO_INC   0x80u

#define CHIP_WHO_AM_I_VALUE 0x33u

/* --- CTRL1 --------------------------------------------------------------- */
#define CTRL1_ODR_MASK      0xF0u
#define CTRL1_ODR_SHIFT     4u
#define CTRL1_LPEN          (1u << 3) /* режим низької роздільності          */
#define CTRL1_ZEN           (1u << 2)
#define CTRL1_YEN           (1u << 1)
#define CTRL1_XEN           (1u << 0)
#define CTRL1_XYZ_EN        (CTRL1_XEN | CTRL1_YEN | CTRL1_ZEN)

#define CHIP_ODR_POWER_DOWN 0x0u
#define CHIP_ODR_100_HZ     0x5u

/* --- CTRL4 --------------------------------------------------------------- */
#define CTRL4_BDU           (1u << 7) /* блокування оновлення блоку даних    */
#define CTRL4_FS_MASK       0x30u
#define CTRL4_FS_SHIFT      4u
#define CTRL4_HR            (1u << 3) /* повна 16-бітна роздільність         */

/* --- STATUS -------------------------------------------------------------- */
#define STATUS_ZYXDA        (1u << 3) /* готові нові дані по всіх трьох осях */
#define STATUS_ZYXOR        (1u << 7) /* попередній відлік не встигли забрати*/

/* Прискорення вільного падіння — єдина константа переходу до SI. */
#define CHIP_G_M_S2         9.80665f

/* Кодування поля FS для діапазонів ±2/±4/±8/±16 g. Повертає 0xFF, якщо
 * діапазон недозволений: викликач мусить це перевірити. */
static inline uint8_t chip_range_to_fs(uint8_t range_g)
{
    switch (range_g) {
    case 2:  return 0u;
    case 4:  return 1u;
    case 8:  return 2u;
    case 16: return 3u;
    default: return 0xFFu;
    }
}

/* Ціна одного відліку в м/с². У режимі повної роздільності шкала ±range_g
 * розкладена на весь 16-бітний знаковий діапазон, тому 1 g при ±2 g — це
 * рівно 16384 відліки. */
static inline float chip_scale_si(uint8_t range_g)
{
    return ((float)range_g * CHIP_G_M_S2) / 32768.0f;
}

#endif /* CHIP_REGS_H */
