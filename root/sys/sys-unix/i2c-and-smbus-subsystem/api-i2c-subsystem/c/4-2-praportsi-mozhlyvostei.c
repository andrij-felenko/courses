#define I2C_FUNC_I2C                    0x00000001 /* Підтримка сирих i2c_msg */
#define I2C_FUNC_10BIT_ADDR             0x00000002 /* 10-бітна адресація */
#define I2C_FUNC_PROTOCOL_MANGLING      0x00000004 /* Підтримка прапорців модифікації протоколу */
#define I2C_FUNC_SMBUS_PEC              0x00000008 /* Апаратна генерація та перевірка PEC CRC-8 */
#define I2C_FUNC_NOSTART                0x00000010 /* Підтримка прапорця I2C_M_NOSTART */
#define I2C_FUNC_SLAVE                  0x00000020 /* Підтримка режиму веденого пристрою */
#define I2C_FUNC_SMBUS_QUICK            0x00010000 /* Quick Command (0 байтів даних) */
#define I2C_FUNC_SMBUS_READ_BYTE        0x00020000 /* Receive Byte */
#define I2C_FUNC_SMBUS_WRITE_BYTE       0x00040000 /* Send Byte */
#define I2C_FUNC_SMBUS_READ_BYTE_DATA   0x00080000 /* Read Byte Data */
#define I2C_FUNC_SMBUS_WRITE_BYTE_DATA  0x00100000 /* Write Byte Data */
#define I2C_FUNC_SMBUS_READ_WORD_DATA   0x00200000 /* Read Word Data */
#define I2C_FUNC_SMBUS_WRITE_WORD_DATA  0x00400000 /* Write Word Data */
#define I2C_FUNC_SMBUS_PROC_CALL        0x00800000 /* Process Call */
#define I2C_FUNC_SMBUS_READ_BLOCK_DATA  0x01000000 /* Block Read з лічильником */
#define I2C_FUNC_SMBUS_WRITE_BLOCK_DATA 0x02000000 /* Block Write з лічильником */
#define I2C_FUNC_SMBUS_READ_I2C_BLOCK   0x04000000 /* I2C Block Read */
#define I2C_FUNC_SMBUS_WRITE_I2C_BLOCK  0x08000000 /* I2C Block Write */

#define I2C_FUNC_SMBUS_EMUL             (I2C_FUNC_SMBUS_QUICK | \
					 I2C_FUNC_SMBUS_BYTE | \
					 I2C_FUNC_SMBUS_BYTE_DATA | \
					 I2C_FUNC_SMBUS_WORD_DATA | \
					 I2C_FUNC_SMBUS_PROC_CALL | \
					 I2C_FUNC_SMBUS_WRITE_BLOCK_DATA | \
					 I2C_FUNC_SMBUS_I2C_BLOCK | \
					 I2C_FUNC_SMBUS_PEC)
