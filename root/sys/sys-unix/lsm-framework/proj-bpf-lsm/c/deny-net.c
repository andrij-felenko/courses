/* deny-net.c — завантажувач мовою C, libbpf */
#include <sys/stat.h>
#include <stdio.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "deny-net.skel.h"

int main(int argc, char **argv)
{
	struct deny_net_bpf *skel;
	struct stat st;
	__u64 cg;
	__u8 one = 1;

	if (argc != 2 || stat(argv[1], &st)) {
		fprintf(stderr, "вжиток: %s /sys/fs/cgroup/<тека>\n", argv[0]);
		return 1;
	}
	cg = st.st_ino;

	skel = deny_net_bpf__open_and_load();
	if (!skel) {
		fprintf(stderr, "перевіряльник не пропустив\n");
		return 1;
	}

	if (bpf_map__update_elem(skel->maps.caged, &cg, sizeof(cg),
				 &one, sizeof(one), BPF_ANY) ||
	    deny_net_bpf__attach(skel)) {
		fprintf(stderr, "не причепилось\n");
		deny_net_bpf__destroy(skel);
		return 1;
	}

	printf("правило діє для cgroup %llu; Ctrl-C знімає\n",
	       (unsigned long long)cg);
	pause();

	deny_net_bpf__destroy(skel);
	return 0;
}
