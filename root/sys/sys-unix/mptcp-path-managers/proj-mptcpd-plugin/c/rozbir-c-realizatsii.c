/* C Implementation: Modern mptcpd plugin */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <mptcpd/plugin.h>
#include <mptcpd/pm.h>

static void handle_new_address(struct mptcpd_pm *pm,
                               uint32_t token,
                               mptcpd_aid_t remote_id,
                               struct sockaddr const *remote_addr,
                               void *user_data)
{
    (void)user_data;
    char ip_str[INET6_ADDRSTRLEN] = {0};
    uint16_t port = 0;

    if (remote_addr->sa_family == AF_INET) {
        struct sockaddr_in const *in = (struct sockaddr_in const *)remote_addr;
        inet_ntop(AF_INET, &in->sin_addr, ip_str, sizeof(ip_str));
        port = ntohs(in->sin_port);
    } else if (remote_addr->sa_family == AF_INET6) {
        struct sockaddr_in6 const *in6 = (struct sockaddr_in6 const *)remote_addr;
        inet_ntop(AF_INET6, &in6->sin6_addr, ip_str, sizeof(ip_str));
        port = ntohs(in6->sin6_port);
    }

    printf("[mptcpd-c-plugin] Connection 0x%08x: New remote address ID %u -> %s:%u\n",
           token, remote_id, ip_str, port);

    /* Фільтрація безпеки: ігнорувати оголошення з тестових мереж 192.168.99.0/24 */
    if (strncmp(ip_str, "192.168.99.", 11) == 0) {
        printf("[mptcpd-c-plugin] Ignoring address %s per security filter\n", ip_str);
        return;
    }

    /* Наказ ядру створити новий підпотік з локального ID 0 */
    mptcpd_aid_t const local_id = 0;
    struct sockaddr_in local_addr;
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = INADDR_ANY;

    int const error = mptcpd_pm_add_subflow(pm,
                                            token,
                                            local_id,
                                            remote_id,
                                            (struct sockaddr const *)&local_addr,
                                            remote_addr,
                                            false); /* backup = false */

    if (error != 0) {
        fprintf(stderr, "[mptcpd-c-plugin] Failed to order subflow creation: %s\n",
                strerror(error));
    }
}

static struct mptcpd_plugin_ops const pm_ops = {
    .new_address = handle_new_address
};

MPTCPD_PLUGIN_REGISTER(c_custom_policy, &pm_ops, NULL, NULL)
