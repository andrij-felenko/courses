// Розшифровка дампу в текст: заради цього все й затівалося — щоб причина була
// видна з першого погляду в терміналі, а не після години з даташитом.
#ifndef FAULT_REPORT_H
#define FAULT_REPORT_H

#include <stdint.h>

#include "crash_dump.h"

// rcc_csr — знімок RCC->CSR, зроблений на самому початку main() до RMVF.
void fault_report_reset_cause(uint32_t rcc_csr);

// Друкує кадр, розібрані біти CFSR/HFSR і адреси MMFAR/BFAR, якщо вони дійсні.
void fault_report_dump(const crash_dump_t *dump);

#endif // FAULT_REPORT_H
