#include <stdint.h>
#include <stdbool.h>

/* Коди результатів виконання функцій HARQ API */
typedef enum {
    HARQ_OK = 0,
    HARQ_ERR_INVALID_PROCESS_ID,
    HARQ_ERR_NO_FREE_PROCESS,
    HARQ_ERR_BUFFER_OVERFLOW,
    HARQ_ERR_OUT_OF_SYNC_NDI,
    HARQ_ERR_MAX_RETRIES_REACHED
} HarqResult;

/* Ініціалізація сутності HARQ для конкретного користувацького термінала (UE) */
HarqResult harq_entity_init(uint16_t rnti, uint8_t num_processes, uint32_t total_soft_buffer_bytes);

/* Виділення вільного процесу HARQ для передачі нового блоку */
HarqResult harq_tx_allocate_process(uint16_t rnti, uint8_t *allocated_pid);

/* Підготовка дескриптора передачі (оновлює RV, інвертує NDI за потреби) */
HarqResult harq_tx_prepare_pdu(uint16_t rnti, uint8_t process_id, bool is_new_data, 
                              const uint8_t *payload, uint32_t tbs, HarqTxProcessDescriptor *out_desc);

/* Обробка отриманого сигналу зворотного зв'язку ACK/NACK/DTX від приймача */
HarqResult harq_tx_handle_feedback(uint16_t rnti, uint8_t process_id, HarqFeedback feedback);

/* Виконання софт-комбінування на приймачі (PHY LLR Combining) */
HarqResult harq_rx_combine_and_decode(uint16_t rnti, uint8_t process_id, bool received_ndi,
                                      HarqRedundancyVersion rv, const int8_t *rx_llr, 
                                      uint32_t llr_count, uint8_t *out_payload, bool *out_crc_pass);

/* Примусове скидання та очищення буфера процесу */
HarqResult harq_process_reset(uint16_t rnti, uint8_t process_id);
