/* cli_license.h — команди `license` та `about` службової консолі. */
#ifndef CLI_LICENSE_H
#define CLI_LICENSE_H

#include "console.h"

/* `license`            — таблиця компонентів;
 * `license mbed`       — картка одного компонента з повним застереженням. */
cli_status_t cli_cmd_license(const char *args, cli_out_fn out);

/* `about` — виріб, версія прошивки й SHA-256 паспорта SBOM цієї збірки. */
cli_status_t cli_cmd_about(const char *args, cli_out_fn out);

#endif /* CLI_LICENSE_H */
