#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TS_PACKET_SIZE       188
#define TS_SYNC_BYTE         0x47
#define TS_MAX_PIDS          8192
#define MAX_ES_STREAMS       16

typedef struct {
    uint8_t  stream_type;
    uint16_t pid;
} ElementaryStream;

typedef struct {
    uint16_t program_number;
    uint16_t pmt_pid;
    uint16_t pcr_pid;
    uint8_t  es_count;
    ElementaryStream streams[MAX_ES_STREAMS];
} ProgramInfo;

typedef struct {
    int8_t   last_cc[TS_MAX_PIDS];
    bool     pid_seen[TS_MAX_PIDS];
    uint32_t packet_count;
    uint32_t dropped_packets;

    ProgramInfo program;
    bool        has_pat;
    bool        has_pmt;
} TsDemuxer;

void ts_demuxer_init(TsDemuxer *demux) {
    memset(demux, 0, sizeof(TsDemuxer));
    for (int i = 0; i < TS_MAX_PIDS; ++i) {
        demux->last_cc[i] = -1;
    }
}

static uint64_t parse_pcr(const uint8_t *buf) {
    uint64_t base = ((uint64_t)buf[0] << 25) |
                    ((uint64_t)buf[1] << 17) |
                    ((uint64_t)buf[2] << 9)  |
                    ((uint64_t)buf[3] << 1)  |
                    ((uint64_t)(buf[4] & 0x80) >> 7);
    uint16_t ext = ((uint16_t)(buf[4] & 0x01) << 8) | buf[5];
    return base * 300 + ext;
}

static uint64_t parse_pts(const uint8_t *buf) {
    uint64_t pts = ((uint64_t)(buf[0] & 0x0E) << 29) |
                   ((uint64_t)buf[1] << 22) |
                   ((uint64_t)(buf[2] & 0xFE) << 14) |
                   ((uint64_t)buf[3] << 7) |
                   ((uint64_t)(buf[4] & 0xFE) >> 1);
    return pts;
}

static void parse_pat(TsDemuxer *demux, const uint8_t *payload, size_t len) {
    if (len < 8) return;
    uint8_t pointer = payload[0];
    const uint8_t *sec = payload + 1 + pointer;
    if (sec + 8 > payload + len) return;

    uint8_t table_id = sec[0];
    if (table_id != 0x00) return;

    uint16_t sec_len = (((uint16_t)(sec[1] & 0x0F)) << 8) | sec[2];
    if (sec_len < 9 || sec + 3 + sec_len > payload + len) return;

    const uint8_t *ptr = sec + 8;
    const uint8_t *end = sec + 3 + sec_len - 4; // Мінус 4 байти CRC32

    while (ptr + 4 <= end) {
        uint16_t prog_num = ((uint16_t)ptr[0] << 8) | ptr[1];
        uint16_t pmt_pid = (((uint16_t)(ptr[2] & 0x1F)) << 8) | ptr[3];
        if (prog_num != 0) { // 0x0000 — це NIT
            demux->program.program_number = prog_num;
            demux->program.pmt_pid = pmt_pid;
            demux->has_pat = true;
            printf("[PAT] Знайдено програму %u -> PMT PID: 0x%04X (%u)\n", prog_num, pmt_pid, pmt_pid);
            break;
        }
        ptr += 4;
    }
}

static void parse_pmt(TsDemuxer *demux, const uint8_t *payload, size_t len) {
    if (len < 12) return;
    uint8_t pointer = payload[0];
    const uint8_t *sec = payload + 1 + pointer;
    if (sec + 12 > payload + len) return;

    uint8_t table_id = sec[0];
    if (table_id != 0x02) return;

    uint16_t sec_len = (((uint16_t)(sec[1] & 0x0F)) << 8) | sec[2];
    if (sec_len < 13 || sec + 3 + sec_len > payload + len) return;

    demux->program.pcr_pid = (((uint16_t)(sec[8] & 0x1F)) << 8) | sec[9];
    uint16_t prog_info_len = (((uint16_t)(sec[10] & 0x0F)) << 8) | sec[11];

    const uint8_t *ptr = sec + 12 + prog_info_len;
    const uint8_t *end = sec + 3 + sec_len - 4; // Мінус 4 байти CRC32

    demux->program.es_count = 0;
    while (ptr + 5 <= end && demux->program.es_count < MAX_ES_STREAMS) {
        uint8_t stream_type = ptr[0];
        uint16_t elem_pid = (((uint16_t)(ptr[1] & 0x1F)) << 8) | ptr[2];
        uint16_t es_info_len = (((uint16_t)(ptr[3] & 0x0F)) << 8) | ptr[4];

        demux->program.streams[demux->program.es_count].stream_type = stream_type;
        demux->program.streams[demux->program.es_count].pid = elem_pid;
        demux->program.es_count++;

        printf("[PMT] Потік #%u: Тип 0x%02X, PID 0x%04X (%u)\n",
               demux->program.es_count, stream_type, elem_pid, elem_pid);

        ptr += 5 + es_info_len;
    }
    demux->has_pmt = true;
}

void ts_demuxer_parse_packet(TsDemuxer *demux, const uint8_t *pkt) {
    if (pkt[0] != TS_SYNC_BYTE) {
        return;
    }
    demux->packet_count++;

    bool tei = (pkt[1] & 0x80) != 0;
    if (tei) {
        demux->dropped_packets++;
        return; // Помилка радіоканалу, пакет пошкоджено
    }

    bool pusi = (pkt[1] & 0x40) != 0;
    uint16_t pid = (((uint16_t)(pkt[1] & 0x1F)) << 8) | pkt[2];
    uint8_t afc = (pkt[3] >> 4) & 0x03;
    uint8_t cc = pkt[3] & 0x0F;

    // Перевірка неперервності Continuity Counter для пакетів із корисними даними
    bool has_payload = (afc == 0x01 || afc == 0x03);
    if (has_payload && pid != 0x1FFF) {
        if (demux->pid_seen[pid]) {
            uint8_t expected_cc = (demux->last_cc[pid] + 1) & 0x0F;
            if (cc != expected_cc && cc != demux->last_cc[pid]) {
                uint8_t lost = (cc >= expected_cc) ? (cc - expected_cc) : (16 + cc - expected_cc);
                demux->dropped_packets += lost;
                printf("[ВТРАТА] PID 0x%04X: втрачено %u пакетів (CC очік: %u, отримано: %u)\n",
                       pid, lost, expected_cc, cc);
            }
        }
        demux->pid_seen[pid] = true;
        demux->last_cc[pid] = cc;
    }

    size_t offset = 4;
    // Обробка адаптаційного поля
    if (afc == 0x02 || afc == 0x03) {
        uint8_t af_len = pkt[offset];
        if (af_len > 0 && offset + 1 + af_len <= TS_PACKET_SIZE) {
            uint8_t flags = pkt[offset + 1];
            bool has_pcr = (flags & 0x10) != 0;
            if (has_pcr && af_len >= 7) {
                uint64_t pcr = parse_pcr(pkt + offset + 2);
                if (demux->has_pmt && pid == demux->program.pcr_pid) {
                    double pcr_sec = (double)pcr / 27000000.0;
                    if (demux->packet_count % 1000 == 0) {
                        printf("[PCR] PID 0x%04X: %.3f с (%llu відліків)\n", pid, pcr_sec, (unsigned long long)pcr);
                    }
                }
            }
        }
        offset += 1 + af_len;
    }

    if (!has_payload || offset >= TS_PACKET_SIZE) return;
    const uint8_t *payload = pkt + offset;
    size_t payload_len = TS_PACKET_SIZE - offset;

    // Маршрутизація згідно з виявленими PID
    if (pid == 0x0000) {
        parse_pat(demux, payload, payload_len);
    } else if (demux->has_pat && pid == demux->program.pmt_pid) {
        parse_pmt(demux, payload, payload_len);
    } else if (pusi && payload_len >= 9) {
        // Початок нового кадру PES
        if (payload[0] == 0x00 && payload[1] == 0x00 && payload[2] == 0x01) {
            uint8_t stream_id = payload[3];
            uint8_t pts_flags = (payload[7] >> 6) & 0x03;
            if ((pts_flags & 0x02) != 0 && payload_len >= 14) {
                uint64_t pts = parse_pts(payload + 9);
                double pts_sec = (double)pts / 90000.0;
                printf("[PES] PID 0x%04X (StreamID 0x%02X) новий кадр: PTS = %.3f с\n",
                       pid, stream_id, pts_sec);
            }
        }
    }
}
