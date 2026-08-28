#define _GNU_SOURCE
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>

/* int statx(int dirfd, const char *path, int flags,
             unsigned int mask, struct statx *buf);      */

/* include/uapi/linux/stat.h */
#define STATX_ATTR_DAX  0x00200000      /* з ядра 5.8 */

int main(int argc, char **argv) {
	struct statx st;
	if (statx(AT_FDCWD, argv[1], AT_STATX_SYNC_AS_STAT,
	          STATX_BASIC_STATS, &st) < 0)
		return perror("statx"), 1;

	if (!(st.stx_attributes_mask & STATX_ATTR_DAX)) {
		puts("ядро або ця ФС про DAX нічого не кажуть");
		return 0;
	}
	puts(st.stx_attributes & STATX_ATTR_DAX ? "S_DAX: так" : "S_DAX: ні");
	return 0;
}
