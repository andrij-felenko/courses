#include "at_queue.h"

#include <string.h>

#include "at_port.h"

const char *at_status_str(at_status_t status)
{
    switch (status) {
        case AT_STATUS_OK:      return "OK";
        case AT_STATUS_ERROR:   return "ERROR";
        case AT_STATUS_TIMEOUT: return "TIMEOUT";
        case AT_STATUS_ABORTED: return "ABORTED";
        default:                return "?";
    }
}

void at_queue_init(at_queue_t *q)
{
    memset(q, 0, sizeof(*q));
}

static bool copy_bounded(char *dst, size_t dst_size, const char *src)
{
    if (src == NULL) {
        dst[0] = '\0';
        return true;
    }
    const size_t len = strlen(src);
    if (len >= dst_size) {
        return false;
    }
    memcpy(dst, src, len + 1U);
    return true;
}

bool at_queue_push(at_queue_t *q, const at_request_t *req)
{
    if (req == NULL || req->text == NULL) {
        return false;
    }
    /* Запрошення без даних — помилка виклику: рушій вишле '>' і зависне. */
    if (req->wait_prompt && (req->payload == NULL || req->payload_len == 0U)) {
        return false;
    }

    at_cmd_t staged;
    memset(&staged, 0, sizeof(staged));

    if (!copy_bounded(staged.text, sizeof(staged.text), req->text)) {
        return false;
    }
    if (!copy_bounded(staged.expect_prefix, sizeof(staged.expect_prefix), req->expect_prefix)) {
        return false;
    }

    staged.payload     = req->payload;
    staged.payload_len = req->payload_len;
    staged.timeout_ms  = (req->timeout_ms != 0U) ? req->timeout_ms : 1000U;
    staged.max_retries = req->retries;
    staged.attempt     = 0U;
    staged.wait_prompt = req->wait_prompt;
    staged.done        = req->done;
    staged.ctx         = req->ctx;

    /* Копіювання зроблено ПОЗА критичною секцією — під вимкненими
       перериваннями лишається тільки рух індексів. */
    const uint32_t saved = at_port_enter_critical();

    if (q->count >= AT_QUEUE_CAPACITY) {
        at_port_exit_critical(saved);
        return false;
    }
    q->item[q->head] = staged;
    q->head  = (uint8_t)((q->head + 1U) % AT_QUEUE_CAPACITY);
    q->count = (uint8_t)(q->count + 1U);

    at_port_exit_critical(saved);
    return true;
}

bool at_queue_pop(at_queue_t *q, at_cmd_t *out)
{
    const uint32_t saved = at_port_enter_critical();

    if (q->count == 0U) {
        at_port_exit_critical(saved);
        return false;
    }
    *out = q->item[q->tail];
    q->tail  = (uint8_t)((q->tail + 1U) % AT_QUEUE_CAPACITY);
    q->count = (uint8_t)(q->count - 1U);

    at_port_exit_critical(saved);
    return true;
}
