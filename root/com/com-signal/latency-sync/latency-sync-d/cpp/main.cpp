// усе в мікросекундах від одного джерела часу (внутрішній годинник МК)
const uint32_t now_us       = 1000000;   // горизонт IMU «зараз»
const uint32_t gps_delay_us =  110000;   // паспортна затримка GPS  (110 мс)
const uint32_t odo_delay_us =   35000;   // затримка одометрії      (35 мс)

// 1) фактичний момент кожного виміру = мітка − затримка потоку
uint32_t gps_meas_us = gps_stamp_us - gps_delay_us;   // коли GPS реально «бачив»
uint32_t odo_meas_us = odo_stamp_us - odo_delay_us;   // коли одометрія «бачила»

// 2) наскільки в минуле відмотати буфер від «зараз»
uint32_t gps_age_us  = now_us - gps_meas_us;          // вік відліку GPS
uint32_t odo_age_us  = now_us - odo_meas_us;          // вік відліку одометрії
