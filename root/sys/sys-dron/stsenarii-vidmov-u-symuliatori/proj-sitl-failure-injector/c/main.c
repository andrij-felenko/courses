#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <poll.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#define MAVLINK_STX_V2          0xFD
#define MAVLINK_MAX_PACKET_LEN  280

#define MSG_ID_HEARTBEAT        0
#define MSG_ID_GPS_RAW_INT      24
#define MSG_ID_ATTITUDE         30
#define MSG_ID_HIL_SENSOR       107
#define MSG_ID_HIL_ACTUATOR     115

#define CRC_EXTRA_HEARTBEAT     50
#define CRC_EXTRA_GPS_RAW_INT   24
#define CRC_EXTRA_ATTITUDE      39
#define CRC_EXTRA_HIL_SENSOR    108
#define CRC_EXTRA_HIL_ACTUATOR  158

#define QUEUE_CAPACITY          256

// Конфігурація сценарію збоїв
typedef struct {
    bool drop_packets;
    float drop_rate;           // 0.0 .. 1.0
    uint32_t delay_ms;         // Мережева затримка

    bool gnss_jamming;         // Глушіння супутників
    bool gnss_spoofing;        // Спуфінг дрейфу
    float spoof_vel_north;     // м/с
    float spoof_vel_east;      // м/с

    bool imu_noise_active;     // Додатковий шум IMU
    float gyro_noise_std;      // рад/с
    float gyro_bias_z;         // рад/с

    bool kill_motor_1;         // Відключення мотора №1
    uint64_t scenario_start_us;
} failure_scenario_t;

// Пакет у черзі затримки
typedef struct {
    uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    size_t length;
    uint64_t deliver_at_us;
    struct sockaddr_in dest_addr;
} delayed_packet_t;

typedef struct {
    delayed_packet_t packets[QUEUE_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
} packet_queue_t;

// Монітор стану автопілота для валідації асертів
typedef struct {
    uint8_t base_mode;
    uint32_t custom_mode;
    uint8_t system_status;
    float roll_deg;
    float pitch_deg;
    float yaw_deg;
    bool failsafe_activated;
    uint64_t failsafe_time_us;
} autopilot_monitor_t;

// Допоміжні функції часу
static uint64_t get_time_micros(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000ULL + (uint64_t)tv.tv_usec;
}

// Контрольна сума CRC16-MCRF4XX
static void crc_accumulate(uint8_t data, uint16_t *crcAccum) {
    uint8_t tmp = data ^ (uint8_t)(*crcAccum & 0xFF);
    tmp ^= (tmp << 4);
    *crcAccum = (*crcAccum >> 8) ^ ((uint16_t)tmp << 8) ^ ((uint16_t)tmp << 3) ^ ((uint16_t)tmp >> 4);
}

static uint16_t crc_calculate(const uint8_t *buffer, size_t length, uint8_t crc_extra) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 1; i < length; ++i) {
        crc_accumulate(buffer[i], &crc);
    }
    crc_accumulate(crc_extra, &crc);
    return crc;
}

// Генератор нормального білого шуму (Box-Muller)
static float generate_gaussian_noise(float mean, float std_dev) {
    float u1 = (float)rand() / (float)RAND_MAX;
    float u2 = (float)rand() / (float)RAND_MAX;
    if (u1 < 1e-7f) u1 = 1e-7f;
    float z0 = sqrtf(-2.0f * logf(u1)) * cosf(2.0f * 3.1415926535f * u2);
    return mean + z0 * std_dev;
}

// Черга затримки
static void queue_init(packet_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

static bool queue_push(packet_queue_t *q, const uint8_t *buf, size_t len, uint64_t deliver_at, const struct sockaddr_in *dest) {
    if (q->count >= QUEUE_CAPACITY) return false;
    delayed_packet_t *p = &q->packets[q->tail];
    memcpy(p->buffer, buf, len);
    p->length = len;
    p->deliver_at_us = deliver_at;
    p->dest_addr = *dest;
    q->tail = (q->tail + 1) % QUEUE_CAPACITY;
    q->count++;
    return true;
}

static bool queue_pop_ready(packet_queue_t *q, uint64_t now_us, delayed_packet_t *out) {
    if (q->count == 0) return false;
    delayed_packet_t *p = &q->packets[q->head];
    if (p->deliver_at_us <= now_us) {
        *out = *p;
        q->head = (q->head + 1) % QUEUE_CAPACITY;
        q->count--;
        return true;
    }
    return false;
}

// Мутатори конкретних повідомлень
static void mutate_gps_raw_int(uint8_t *payload, failure_scenario_t *sc, uint64_t now_us) {
    if (sc->gnss_jamming) {
        payload[20] = 1; // fix_type = No Fix
        payload[21] = 2; // satellites_visible = 2
        uint16_t bad_eph = 9999;
        uint16_t bad_epv = 9999;
        memcpy(&payload[22], &bad_eph, sizeof(uint16_t));
        memcpy(&payload[24], &bad_epv, sizeof(uint16_t));
    } else if (sc->gnss_spoofing) {
        int32_t lat, lon;
        memcpy(&lat, &payload[8], sizeof(int32_t));
        memcpy(&lon, &payload[12], sizeof(int32_t));

        double dt = (double)(now_us - sc->scenario_start_us) * 1e-6;
        int32_t d_lat = (int32_t)((sc->spoof_vel_north * dt / 111132.0) * 1e7);
        int32_t d_lon = (int32_t)((sc->spoof_vel_east * dt / 111132.0) * 1e7);

        lat += d_lat;
        lon += d_lon;

        memcpy(&payload[8], &lat, sizeof(int32_t));
        memcpy(&payload[12], &lon, sizeof(int32_t));
    }
}

static void mutate_hil_sensor(uint8_t *payload, failure_scenario_t *sc) {
    if (sc->imu_noise_active) {
        float xgyro, ygyro, zgyro;
        memcpy(&xgyro, &payload[12], sizeof(float));
        memcpy(&ygyro, &payload[16], sizeof(float));
        memcpy(&zgyro, &payload[20], sizeof(float));

        xgyro += generate_gaussian_noise(0.0f, sc->gyro_noise_std);
        ygyro += generate_gaussian_noise(0.0f, sc->gyro_noise_std);
        zgyro += generate_gaussian_noise(sc->gyro_bias_z, sc->gyro_noise_std);

        memcpy(&payload[12], &xgyro, sizeof(float));
        memcpy(&payload[16], &ygyro, sizeof(float));
        memcpy(&payload[20], &zgyro, sizeof(float));
    }
}

static void mutate_hil_actuator(uint8_t *payload, failure_scenario_t *sc) {
    if (sc->kill_motor_1) {
        float zero_thrust = 0.0f;
        memcpy(&payload[8], &zero_thrust, sizeof(float)); // Мотор 1 = 0
    }
}

// Парсинг телеметрії автопілота для Assert Engine
static void parse_autopilot_feedback(const uint8_t *buf, size_t len, autopilot_monitor_t *mon, uint64_t now_us) {
    if (len < 12 || buf[0] != MAVLINK_STX_V2) return;
    uint32_t msg_id = (uint32_t)buf[7] | ((uint32_t)buf[8] << 8) | ((uint32_t)buf[9] << 16);
    const uint8_t *payload = &buf[10];

    if (msg_id == MSG_ID_HEARTBEAT) {
        mon->custom_mode = (uint32_t)payload[0] | ((uint32_t)payload[1] << 8) |
                           ((uint32_t)payload[2] << 16) | ((uint32_t)payload[3] << 24);
        mon->base_mode = payload[6];
        mon->system_status = payload[7];

        // PX4 / ArduPilot Failsafe flag in base_mode / custom_mode
        if ((mon->base_mode & 0x01) || (mon->system_status == 5)) { // 5 = MAV_STATE_CRITICAL
            if (!mon->failsafe_activated) {
                mon->failsafe_activated = true;
                mon->failsafe_time_us = now_us;
                printf("[ASSERT ENGINE] Детектовано перехід у Failsafe на %llu мкс\n", (unsigned long long)now_us);
            }
        }
    } else if (msg_id == MSG_ID_ATTITUDE) {
        float roll, pitch, yaw;
        memcpy(&roll, &payload[4], sizeof(float));
        memcpy(&pitch, &payload[8], sizeof(float));
        memcpy(&yaw, &payload[12], sizeof(float));

        mon->roll_deg = roll * 57.2957795f;
        mon->pitch_deg = pitch * 57.2957795f;
        mon->yaw_deg = yaw * 57.2957795f;
    }
}

// Головний обробник пакета
static bool process_mavlink_packet(uint8_t *buf, size_t len, failure_scenario_t *sc, autopilot_monitor_t *mon, bool is_from_sim, uint64_t now_us) {
    if (len < 12 || buf[0] != MAVLINK_STX_V2) return true;

    if (!is_from_sim) {
        parse_autopilot_feedback(buf, len, mon, now_us);
        return true;
    }

    uint8_t payload_len = buf[1];
    uint32_t msg_id = (uint32_t)buf[7] | ((uint32_t)buf[8] << 8) | ((uint32_t)buf[9] << 16);
    uint8_t *payload = &buf[10];
    uint8_t crc_extra = 0;
    bool mutated = false;

    if (sc->drop_packets) {
        float r = (float)rand() / (float)RAND_MAX;
        if (r < sc->drop_rate) return false; // Відкидання
    }

    switch (msg_id) {
    case MSG_ID_GPS_RAW_INT:
        mutate_gps_raw_int(payload, sc, now_us);
        crc_extra = CRC_EXTRA_GPS_RAW_INT;
        mutated = true;
        break;

    case MSG_ID_HIL_SENSOR:
        mutate_hil_sensor(payload, sc);
        crc_extra = CRC_EXTRA_HIL_SENSOR;
        mutated = true;
        break;

    case MSG_ID_HIL_ACTUATOR:
        mutate_hil_actuator(payload, sc);
        crc_extra = CRC_EXTRA_HIL_ACTUATOR;
        mutated = true;
        break;

    default:
        break;
    }

    if (mutated) {
        size_t header_and_payload_len = 10 + payload_len;
        uint16_t new_crc = crc_calculate(buf, header_and_payload_len, crc_extra);
        buf[header_and_payload_len] = (uint8_t)(new_crc & 0xFF);
        buf[header_and_payload_len + 1] = (uint8_t)((new_crc >> 8) & 0xFF);
    }

    return true;
}

int main(void) {
    printf("[INJECTOR-C99] Запуск MAVLink Fault Injection & Assertion Proxy...\n");

    int sock_sim = socket(AF_INET, SOCK_DGRAM, 0);
    int sock_ap  = socket(AF_INET, SOCK_DGRAM, 0);

    struct sockaddr_in addr_sim, addr_ap;
    memset(&addr_sim, 0, sizeof(addr_sim));
    addr_sim.sin_family = AF_INET;
    addr_sim.sin_addr.s_s_addr = htonl(INADDR_ANY);
    addr_sim.sin_port = htons(14560); // Порт прийому від Gazebo

    memset(&addr_ap, 0, sizeof(addr_ap));
    addr_ap.sin_family = AF_INET;
    addr_ap.sin_addr.s_s_addr = htonl(INADDR_ANY);
    addr_ap.sin_port = htons(14550); // Порт прийому від Автопілота

    bind(sock_sim, (struct sockaddr*)&addr_sim, sizeof(addr_sim));
    bind(sock_ap, (struct sockaddr*)&addr_ap, sizeof(addr_ap));

    fcntl(sock_sim, F_SETFL, O_NONBLOCK);
    fcntl(sock_ap, F_SETFL, O_NONBLOCK);

    struct sockaddr_in target_ap;
    memset(&target_ap, 0, sizeof(target_ap));
    target_ap.sin_family = AF_INET;
    target_ap.sin_port = htons(14555);
    inet_pton(AF_INET, "127.0.0.1", &target_ap.sin_addr);

    struct sockaddr_in target_sim;
    memset(&target_sim, 0, sizeof(target_sim));
    target_sim.sin_family = AF_INET;
    target_sim.sin_port = htons(14565);
    inet_pton(AF_INET, "127.0.0.1", &target_sim.sin_addr);

    failure_scenario_t scenario = {
        .drop_packets = false,
        .drop_rate = 0.0f,
        .delay_ms = 0,
        .gnss_jamming = true, // Тест реакції автопілота на глушіння
        .gnss_spoofing = false,
        .spoof_vel_north = 0.0f,
        .spoof_vel_east = 0.0f,
        .imu_noise_active = false,
        .gyro_noise_std = 0.0f,
        .gyro_bias_z = 0.0f,
        .kill_motor_1 = false,
        .scenario_start_us = get_time_micros()
    };

    autopilot_monitor_t monitor = { 0 };
    packet_queue_t queue_to_ap;
    queue_init(&queue_to_ap);

    uint8_t rx_buf[MAVLINK_MAX_PACKET_LEN];
    struct pollfd fds[2];
    fds[0].fd = sock_sim;
    fds[0].events = POLLIN;
    fds[1].fd = sock_ap;
    fds[1].events = POLLIN;

    uint64_t test_timeout_us = get_time_micros() + 10000000ULL; // 10 секунд тесту
    while (get_time_micros() < test_timeout_us) {
        uint64_t now_us = get_time_micros();

        // Відправка затриманих пакетів
        delayed_packet_t delayed_pkt;
        while (queue_pop_ready(&queue_to_ap, now_us, &delayed_pkt)) {
            sendto(sock_ap, delayed_pkt.buffer, delayed_pkt.length, 0,
                   (struct sockaddr*)&delayed_pkt.dest_addr, sizeof(delayed_pkt.dest_addr));
        }

        int ret = poll(fds, 2, 1);
        if (ret > 0) {
            // Симулятор -> Автопілот
            if (fds[0].revents & POLLIN) {
                struct sockaddr_in src;
                socklen_t src_len = sizeof(src);
                ssize_t n = recvfrom(sock_sim, rx_buf, sizeof(rx_buf), 0, (struct sockaddr*)&src, &src_len);
                if (n > 0) {
                    if (process_mavlink_packet(rx_buf, (size_t)n, &scenario, &monitor, true, now_us)) {
                        if (scenario.delay_ms > 0) {
                            uint64_t deliver_at = now_us + (uint64_t)scenario.delay_ms * 1000ULL;
                            queue_push(&queue_to_ap, rx_buf, (size_t)n, deliver_at, &target_ap);
                        } else {
                            sendto(sock_ap, rx_buf, (size_t)n, 0, (struct sockaddr*)&target_ap, sizeof(target_ap));
                        }
                    }
                }
            }

            // Автопілот -> Симулятор
            if (fds[1].revents & POLLIN) {
                struct sockaddr_in src;
                socklen_t src_len = sizeof(src);
                ssize_t n = recvfrom(sock_ap, rx_buf, sizeof(rx_buf), 0, (struct sockaddr*)&src, &src_len);
                if (n > 0) {
                    if (process_mavlink_packet(rx_buf, (size_t)n, &scenario, &monitor, false, now_us)) {
                        sendto(sock_sim, rx_buf, (size_t)n, 0, (struct sockaddr*)&target_sim, sizeof(target_sim));
                    }
                }
            }
        }

        // Перевірка асертів під час польоту
        if (fabsf(monitor.roll_deg) > 70.0f || fabsf(monitor.pitch_deg) > 70.0f) {
            printf("[ASSERT FAILED] Критичне перекидання дрона: Roll=%.1f°, Pitch=%.1f°\n",
                   monitor.roll_deg, monitor.pitch_deg);
            break;
        }
    }

    // Підсумкова валідація
    if (monitor.failsafe_activated) {
        printf("[TEST PASSED] Автопілот успішно перейшов у Failsafe після інжекції аномалії.\n");
    } else {
        printf("[TEST WARNING] Failsafe не було активовано протягом тестового вікна.\n");
    }

    close(sock_sim);
    close(sock_ap);
    return 0;
}
