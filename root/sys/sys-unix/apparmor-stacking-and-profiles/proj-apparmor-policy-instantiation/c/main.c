/* c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/apparmor.h>
#include <sys/stat.h>

#define PROFILE_TEMPLATE \
    "profile %s flags=(attach_disconnected) {\n" \
    "  file,\n" \
    "  deny /etc/shadow rw,\n" \
    "  %s/ r,\n" \
    "  %s/** rw,\n" \
    "}\n"

static int load_profile_to_kernel(const char *profile_text) {
    /* Ядро приймає в .load лише скомпільований образ політики,
       тож текст профілю віддаємо apparmor_parser: він компілює й завантажує сам. */
    FILE *parser = popen("apparmor_parser --quiet --replace", "w");
    if (!parser) {
        perror("Failed to start apparmor_parser");
        return -1;
    }

    size_t len = strlen(profile_text);
    if (fwrite(profile_text, 1, len, parser) != len) {
        fprintf(stderr, "Failed to feed the profile text to apparmor_parser\n");
        pclose(parser);
        return -1;
    }

    int status = pclose(parser);
    if (status != 0) {
        fprintf(stderr, "apparmor_parser exited with status %d\n", status);
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <profile_name> <sandbox_dir>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *prof_name = argv[1];
    const char *sandbox_dir = argv[2];

    char profile_buf[2048];
    snprintf(profile_buf, sizeof(profile_buf), PROFILE_TEMPLATE, prof_name, sandbox_dir, sandbox_dir);

    printf("[C Engine] Instantiating AppArmor profile '%s' for dir '%s'...\n", prof_name, sandbox_dir);

    if (load_profile_to_kernel(profile_buf) < 0) {
        fprintf(stderr, "[C Engine] Error loading instantiated profile.\n");
        return EXIT_FAILURE;
    }

    /* Налаштовуємо стекування профілів під час наступного execve */
    char stack_target[512];
    snprintf(stack_target, sizeof(stack_target), "docker-default//&%s", prof_name);

    printf("[C Engine] Scheduling stacked exec transition to '%s'...\n", stack_target);
    if (aa_change_onexec(stack_target) < 0) {
        perror("[C Engine] aa_change_onexec failed");
        return EXIT_FAILURE;
    }

    /* Запускаємо цільовий процес у стеку */
    char *worker_args[] = { "/bin/bash", "-c", "echo 'Inside sandbox'; id", NULL };
    execvp(worker_args[0], worker_args);

    perror("[C Engine] execvp failed");
    return EXIT_FAILURE;
}
