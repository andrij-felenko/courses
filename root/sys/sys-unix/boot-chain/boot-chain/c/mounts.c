/* Крок 1 фази 5: підготовка дерева монтувань і перенесення службових гілок
 * зі старого кореня в новий. */

#define _GNU_SOURCE
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>

#include "log.h"
#include "steps.h"

/* Ці дерева тримають відкриті дескриптори й активні структури ядра
 * (udev, сокети, консоль), тому їх не демонтують, а переставляють. */
static const char *const kept[] = { "/dev", "/proc", "/sys", "/run" };

int make_mount_tree_private(void)
{
	/* MS_MOVE відмовляє з EINVAL, якщо монтування має спільне поширення
	 * (shared): ядро не знає, куди в такому разі транслювати переміщення
	 * для решти простору імен. Сучасний initramfs успадковує саме shared,
	 * тому перед перенесенням переводимо все піддерево в private. */
	if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) {
		boot_errno("mount(\"/\", MS_REC|MS_PRIVATE)", NULL);
		return -1;
	}
	return 0;
}

/* Точка монтування відрізняється від звичайного каталогу тим, що лежить
 * на іншому пристрої, ніж її батько. */
static int is_mount_point(const char *path)
{
	struct stat self_st, parent_st;
	char parent[PATH_MAX];
	int n;

	if (stat(path, &self_st) != 0 || !S_ISDIR(self_st.st_mode))
		return 0;

	n = snprintf(parent, sizeof parent, "%s/..", path);
	if (n < 0 || (size_t)n >= sizeof parent)
		return 0;
	if (stat(parent, &parent_st) != 0)
		return 0;

	return self_st.st_dev != parent_st.st_dev;
}

/* Якщо перенести не вдалося, монтування треба хоча б відчепити: інакше воно
 * триматиме стару rootfs у пам'яті, і крок стирання не поверне сторінок.
 * MNT_DETACH відчіплює гілку негайно, а звільняє її тоді, коли останній
 * користувач закриє свій дескриптор. */
static void detach(const char *path)
{
	if (umount2(path, MNT_DETACH) != 0)
		boot_errno("umount2(MNT_DETACH)", path);
}

unsigned long move_special_mounts(const char *newroot)
{
	unsigned long failed = 0;
	size_t i;

	for (i = 0; i < sizeof kept / sizeof kept[0]; i++) {
		const char *src = kept[i];
		char dst[PATH_MAX];
		struct stat st;
		int n;

		/* У мінімальному initramfs частини з них може просто не бути. */
		if (!is_mount_point(src))
			continue;

		n = snprintf(dst, sizeof dst, "%s%s", newroot, src);
		if (n < 0 || (size_t)n >= sizeof dst) {
			boot_err("шлях %s%s задовгий", newroot, src);
			detach(src);
			failed++;
			continue;
		}
		/* MS_MOVE вимагає готового каталогу-цілі: створювати його тут
		 * не будемо — його відсутність означає, що змонтовано щось не те. */
		if (stat(dst, &st) != 0 || !S_ISDIR(st.st_mode)) {
			boot_err("у новому корені немає каталогу %s — відчіплюю %s",
				 dst, src);
			detach(src);
			failed++;
			continue;
		}
		/* MS_MOVE переносить гілку цілком, разом з усім, що змонтоване
		 * під нею (/dev/pts, /dev/shm), і не чіпає відкритих файлів. */
		if (mount(src, dst, NULL, MS_MOVE, NULL) != 0) {
			boot_err("MS_MOVE %s → %s: %s", src, dst, strerror(errno));
			detach(src);
			failed++;
		}
	}
	return failed;
}
