#ifndef IIO_VIRTUAL_SENSOR_H
#define IIO_VIRTUAL_SENSOR_H

#include <linux/types.h>
#include <linux/mutex.h>
#include <linux/iio/iio.h>
#include <linux/iio/buffer.h>
#include <linux/iio/triggered_buffer.h>
#include <linux/iio/trigger_consumer.h>

/* Індекси вимірювальних каналів IIO */
enum iio_virtual_channels_idx {
	VIRT_CHAN_ACCEL_X,
	VIRT_CHAN_GYRO_Z,
	VIRT_CHAN_TIMESTAMP,
};

/**
 * struct iio_virtual_scan_data - Вирівняний кадр даних для буфера kfifo.
 * @accel: Сире значення прискорення по осі X (16 біт).
 * @gyro: Сире значення кутової швидкості по осі Z (16 біт).
 * @ts: 64-бітна часова мітка ядра, вирівняна на 8 байтів для DMA/kfifo.
 */
struct iio_virtual_scan_data {
	s16 accel;
	s16 gyro;
	s64 ts __aligned(8);
};

/**
 * struct iio_virtual_dev - Приватний контекст драйвера віртуального IIO-давача.
 * @lock: Мутекс для захисту доступу до внутрішніх даних пристрою.
 * @accel_val: Поточне сире значення прискорення.
 * @gyro_val: Поточне сире значення кутової швидкості.
 * @scale_val: Ціла частина масштабного коефіцієнта.
 * @scale_micro: Дробна частина масштабного коефіцієнта (у мікроодиницях).
 */
struct iio_virtual_dev {
	struct mutex lock;
	s16 accel_val;
	s16 gyro_val;
	int scale_val;
	int scale_micro;
};

/**
 * iio_virtual_buffer_setup() - Налаштовує тригерний буфер IIO для пристрою.
 * @indio_dev: Вказівник на структуру екземпляра IIO-пристрою.
 *
 * Return: 0 у разі успіху або від'ємний код помилки.
 */
int iio_virtual_buffer_setup(struct iio_dev *indio_dev);

#endif /* IIO_VIRTUAL_SENSOR_H */
