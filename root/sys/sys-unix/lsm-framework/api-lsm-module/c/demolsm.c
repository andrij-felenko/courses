// security/demolsm/demolsm.c
// SPDX-License-Identifier: GPL-2.0
#define pr_fmt(fmt) "demolsm: " fmt

#include <linux/cred.h>
#include <linux/lsm_hooks.h>
#include <linux/net.h>
#include <linux/sched.h>
#include <linux/socket.h>
#include <uapi/linux/lsm.h>

static int demolsm_socket_connect(struct socket *sock,
				  struct sockaddr *address, int addrlen)
{
	if (address->sa_family != AF_INET && address->sa_family != AF_INET6)
		return 0;
	if (uid_eq(current_euid(), GLOBAL_ROOT_UID))
		return 0;

	pr_info("connect заборонено, pid %d\n", current->pid);
	return -EPERM;
}

static struct security_hook_list demolsm_hooks[] __ro_after_init = {
	LSM_HOOK_INIT(socket_connect, demolsm_socket_connect),
};

static const struct lsm_id demolsm_lsmid = {
	.name = "demolsm",
	.id   = LSM_ID_UNDEF,	/* свій номер дають лише при вливанні в дерево */
};

static int __init demolsm_init(void)
{
	security_add_hooks(demolsm_hooks, ARRAY_SIZE(demolsm_hooks),
			   &demolsm_lsmid);
	pr_info("піднято\n");
	return 0;
}

DEFINE_LSM(demolsm) = {
	.name = "demolsm",
	.init = demolsm_init,
};
