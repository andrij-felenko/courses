#ifndef VERSION_AUTOGEN_H
#define VERSION_AUTOGEN_H

#include <stdint.h>

#define FW_VERSION_MAJOR        2
#define FW_VERSION_MINOR        4
#define FW_VERSION_PATCH        1
#define FW_SECURITY_COUNTER     5U  /* Підвищено з 4 до 5 для блокування CVE-2026-4419 */
#define FW_COMMIT_HASH_PREFIX   0x7a8f9c4bU
#define FW_VERSION_STRING       "2.4.1-hotfix"

#endif /* VERSION_AUTOGEN_H */
