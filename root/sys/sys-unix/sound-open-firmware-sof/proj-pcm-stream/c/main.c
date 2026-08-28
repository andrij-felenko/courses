/* C implementation of SOF IPC stream emulator */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define SOF_IPC_STREAM_PCM_PARAMS 0x0001
#define SOF_IPC_STREAM_TRIG_START 0x0002
#define SOF_IPC_STREAM_TRIG_STOP  0x0003

struct sof_ipc_cmd_hdr {
    uint32_t size;
    uint32_t cmd;
} __attribute__((packed));

struct sof_ipc_stream_params {
    struct sof_ipc_cmd_hdr hdr;
    uint32_t comp_id;
    uint32_t rate;
    uint32_t channels;
    uint32_t buffer_size;
    uint32_t period_size;
} __attribute__((packed));

struct sof_dsp_ipc_mailbox {
    uint8_t sram_buffer[1024];
    uint32_t doorbell_host_to_dsp;
    uint32_t doorbell_dsp_to_host;
};

struct sof_pcm_stream {
    uint32_t stream_id;
    uint8_t *dma_area;
    size_t dma_bytes;
    size_t period_bytes;
    size_t host_ptr;
    struct sof_dsp_ipc_mailbox *mailbox;
};

int sof_ipc_send_message(struct sof_dsp_ipc_mailbox *mb, const void *msg, size_t msg_len) {
    if (msg_len > sizeof(mb->sram_buffer)) {
        return -1;
    }
    /* Копіювання команди у SRAM Mailbox та дзвінок у Doorbell */
    memcpy(mb->sram_buffer, msg, msg_len);
    mb->doorbell_host_to_dsp = 1;
    
    /* Імітація обробки команди на боці DSP та відповіді */
    mb->doorbell_host_to_dsp = 0;
    mb->doorbell_dsp_to_host = 1;
    return 0;
}

struct sof_pcm_stream *sof_pcm_create(struct sof_dsp_ipc_mailbox *mb, uint32_t rate, uint32_t channels) {
    struct sof_pcm_stream *stream = (struct sof_pcm_stream *)malloc(sizeof(struct sof_pcm_stream));
    if (!stream) return NULL;

    stream->stream_id = 1;
    stream->period_bytes = 4096;
    stream->dma_bytes = stream->period_bytes * 4;
    stream->dma_area = (uint8_t *)calloc(1, stream->dma_bytes);
    if (!stream->dma_area) {
        free(stream);
        return NULL;
    }
    stream->host_ptr = 0;
    stream->mailbox = mb;

    struct sof_ipc_stream_params params;
    memset(&params, 0, sizeof(params));
    params.hdr.size = sizeof(params);
    params.hdr.cmd = SOF_IPC_STREAM_PCM_PARAMS;
    params.comp_id = stream->stream_id;
    params.rate = rate;
    params.channels = channels;
    params.buffer_size = (uint32_t)stream->dma_bytes;
    params.period_size = (uint32_t)stream->period_bytes;

    if (sof_ipc_send_message(mb, &params, sizeof(params)) != 0) {
        free(stream->dma_area);
        free(stream);
        return NULL;
    }

    printf("[SOF C] Stream %u configured: %u Hz, %u ch, buffer %zu B\n",
           stream->stream_id, rate, channels, stream->dma_bytes);
    return stream;
}

void sof_pcm_write_samples(struct sof_pcm_stream *stream, const uint8_t *data, size_t count) {
    if (!stream || !data) return;
    
    size_t space = stream->dma_bytes - stream->host_ptr;
    size_t chunk = (count < space) ? count : space;
    
    memcpy(stream->dma_area + stream->host_ptr, data, chunk);
    stream->host_ptr = (stream->host_ptr + chunk) % stream->dma_bytes;
    
    if (count > chunk) {
        size_t remainder = count - chunk;
        memcpy(stream->dma_area, data + chunk, remainder);
        stream->host_ptr = remainder;
    }
}

void sof_pcm_destroy(struct sof_pcm_stream *stream) {
    if (!stream) return;
    free(stream->dma_area);
    free(stream);
}
