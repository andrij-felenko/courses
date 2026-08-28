/* Приклад автентифікації консольної програми мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <security/pam_appl.h>

static int sample_conv(int num_msg, const struct pam_message **msg,
                       struct pam_response **resp, void *appdata_ptr) {
    if (num_msg <= 0 || num_msg > PAM_MAX_NUM_MSG) return PAM_CONV_ERR;
    
    struct pam_response *reply = calloc(num_msg, sizeof(struct pam_response));
    if (!reply) return PAM_BUF_ERR;

    for (int i = 0; i < num_msg; ++i) {
        if (msg[i]->msg_style == PAM_PROMPT_ECHO_OFF) {
            printf("%s", msg[i]->msg);
            char buffer[256];
            if (fgets(buffer, sizeof(buffer), stdin)) {
                buffer[strcspn(buffer, "\n")] = '\0';
                reply[i].resp = strdup(buffer);
            }
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

int authenticate_user(const char *username) {
    pam_handle_t *pamh = NULL;
    struct pam_conv conv = { sample_conv, NULL };

    int retval = pam_start("check_service", username, &conv, &pamh);
    if (retval != PAM_SUCCESS) return retval;

    retval = pam_authenticate(pamh, 0);
    if (retval == PAM_SUCCESS) {
        retval = pam_acct_mgmt(pamh, 0);
    }

    pam_end(pamh, retval);
    return retval;
}
