/* Крок 2 фази 5: рекурсивне стирання тимчасової rootfs.
 *
 * Ходимо не шляхами, а дескрипторами каталогів (openat/unlinkat): шлях під
 * нами міг би підмінити симвлінк, а дескриптор указує на конкретний inode. */

#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "log.h"
#include "steps.h"

/* Стирає вміст каталогу dirfd, не виходячи за межі пристрою dev.
 * Дескриптор лишається за викликачем — закривати його тут не можна. */
static unsigned long wipe_contents(int dirfd, dev_t dev)
{
	unsigned long errors = 0;
	struct dirent *entry;
	DIR *dir;
	int copy;

	/* fdopendir забирає дескриптор собі, а він потрібен нам і після обходу. */
	copy = dup(dirfd);
	if (copy < 0) {
		boot_errno("dup", ".");
		return 1;
	}
	dir = fdopendir(copy);
	if (dir == NULL) {
		boot_errno("fdopendir", ".");
		close(copy);
		return 1;
	}

	while ((entry = readdir(dir)) != NULL) {
		struct stat st;
		int sub;

		if (strcmp(entry->d_name, ".") == 0 ||
		    strcmp(entry->d_name, "..") == 0)
			continue;

		if (fstatat(dirfd, entry->d_name, &st, AT_SYMLINK_NOFOLLOW) != 0) {
			boot_errno("fstatat", entry->d_name);
			errors++;
			continue;
		}

		if (!S_ISDIR(st.st_mode)) {
			/* Звичайний файл, симвлінк, сокет, пристрій — просто
			 * відв'язуємо: вміст ramfs зникає разом з останнім
			 * посиланням на нього. */
			if (unlinkat(dirfd, entry->d_name, 0) != 0) {
				boot_errno("unlinkat", entry->d_name);
				errors++;
			}
			continue;
		}

		/* Інший пристрій означає точку монтування: там уже не наша пам'ять.
		 * Саме ця перевірка рятує щойно змонтований /sysroot. */
		if (st.st_dev != dev)
			continue;

		sub = openat(dirfd, entry->d_name,
			     O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
		if (sub < 0) {
			boot_errno("openat", entry->d_name);
			errors++;
			continue;
		}
		errors += wipe_contents(sub, dev);
		close(sub);

		/* Каталог знімається лише після того, як спорожнів: непорожній
		 * дасть ENOTEMPTY, і про це варто сказати вголос. */
		if (unlinkat(dirfd, entry->d_name, AT_REMOVEDIR) != 0) {
			boot_errno("rmdir", entry->d_name);
			errors++;
		}
	}

	closedir(dir);
	return errors;
}

unsigned long wipe_filesystem(int rootfd)
{
	struct stat st;

	if (fstat(rootfd, &st) != 0) {
		boot_errno("fstat", "/");
		return 1;
	}
	/* Знищення метаданих ramfs миттєво повертає сторінки в Buddy Allocator:
	 * там немає ні кешу сторінок, ні відкладеного запису — лише самі дані. */
	return wipe_contents(rootfd, st.st_dev);
}
