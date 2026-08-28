/* typec_switcher.c — C99 implementation using standard POSIX file I/O */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <errno.h>

#define SYSFS_TYPEC_DIR "/sys/class/typec"
#define PATH_BUF_SIZE   512
#define VALUE_BUF_SIZE  64

static int read_sysfs_string(const char *path, char *buf, size_t size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -errno;
    }

    ssize_t ret = read(fd, buf, size - 1);
    int saved_errno = errno;
    close(fd);

    if (ret < 0) {
        return -saved_errno;
    }

    buf[ret] = '\0';
    /* Trim trailing newline character */
    char *nl = strchr(buf, '\n');
    if (nl) {
        *nl = '\0';
    }

    return 0;
}

static int write_sysfs_string(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        perror("Failed to open sysfs attribute for writing");
        return -errno;
    }

    size_t len = strlen(val);
    ssize_t ret = write(fd, val, len);
    int saved_errno = errno;
    close(fd);

    if (ret < 0) {
        errno = saved_errno;
        perror("Failed to write to sysfs attribute");
        return -saved_errno;
    }

    return 0;
}

static void inspect_typec_port(const char *port_name) {
    char path[PATH_BUF_SIZE];
    char data_role[VALUE_BUF_SIZE] = "unknown";
    char power_role[VALUE_BUF_SIZE] = "unknown";
    char port_type[VALUE_BUF_SIZE] = "unknown";
    char partner_path[PATH_BUF_SIZE];

    snprintf(path, sizeof(path), "%s/%s/data_role", SYSFS_TYPEC_DIR, port_name);
    read_sysfs_string(path, data_role, sizeof(data_role));

    snprintf(path, sizeof(path), "%s/%s/power_role", SYSFS_TYPEC_DIR, port_name);
    read_sysfs_string(path, power_role, sizeof(power_role));

    snprintf(path, sizeof(path), "%s/%s/port_type", SYSFS_TYPEC_DIR, port_name);
    read_sysfs_string(path, port_type, sizeof(port_type));

    snprintf(partner_path, sizeof(partner_path), "%s/%s/%s-partner", SYSFS_TYPEC_DIR, port_name, port_name);
    int partner_connected = (access(partner_path, F_OK) == 0);

    printf("=== Port %s ===\n", port_name);
    printf("  Port Type:  %s\n", port_type);
    printf("  Data Role:  %s\n", data_role);
    printf("  Power Role: %s\n", power_role);
    printf("  Partner:    %s\n", partner_connected ? "CONNECTED" : "DISCONNECTED");
}

int main(int argc, char *argv[]) {
    if (argc >= 4 && strcmp(argv[1], "--swap") == 0) {
        const char *port = argv[2];
        const char *target_role = argv[3]; /* host/device or source/sink */
        char path[PATH_BUF_SIZE];

        if (strcmp(target_role, "host") == 0 || strcmp(target_role, "device") == 0) {
            snprintf(path, sizeof(path), "%s/%s/data_role", SYSFS_TYPEC_DIR, port);
        } else if (strcmp(target_role, "source") == 0 || strcmp(target_role, "sink") == 0) {
            snprintf(path, sizeof(path), "%s/%s/power_role", SYSFS_TYPEC_DIR, port);
        } else {
            fprintf(stderr, "Unknown target role: %s\n", target_role);
            return EXIT_FAILURE;
        }

        printf("Requesting swap on %s to %s...\n", port, target_role);
        if (write_sysfs_string(path, target_role) == 0) {
            printf("Swap request submitted successfully.\n");
        } else {
            fprintf(stderr, "Swap request failed!\n");
            return EXIT_FAILURE;
        }
        return EXIT_SUCCESS;
    }

    DIR *dir = opendir(SYSFS_TYPEC_DIR);
    if (!dir) {
        perror("Cannot open /sys/class/typec");
        return EXIT_FAILURE;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, "port", 4) == 0 && strchr(entry->d_name, '-') == NULL) {
            inspect_typec_port(entry->d_name);
        }
    }
    closedir(dir);

    return EXIT_SUCCESS;
}
