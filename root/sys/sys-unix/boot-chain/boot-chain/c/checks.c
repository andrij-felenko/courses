/* Перевірки перед переходом.
 *
 * Усе, що можна дізнатися, поки не зроблено жодної незворотної дії: далі
 * буде стирання пам'яті й підміна кореня, а звідти повернення вже немає.
 * Кожна перевірка коштує один-два системні виклики — ціна помилки на
 * порядки вища.
 */

#define _GNU_SOURCE
#include <errno.h>
#include <limits.h>
#include <linux/magic.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <unistd.h>

#include "log.h"
#include "steps.h"

/* Стара rootfs мусить жити в пам'яті. Якщо ми помилилися і корінь на носії,
 * крок стирання зніс би диск: перевірка коштує один системний виклик. */
static int root_lives_in_memory(void)
{
	struct statfs sb;

	if (statfs("/", &sb) != 0) {
		boot_errno("statfs", "/");
		return 0;
	}
	if ((unsigned long)sb.f_type == RAMFS_MAGIC ||
	    (unsigned long)sb.f_type == TMPFS_MAGIC)
		return 1;

	boot_err("корінь не ramfs і не tmpfs (тип 0x%lx) — стирати його не можна",
		 (unsigned long)sb.f_type);
	return 0;
}

/* Новий корінь мусить бути ОКРЕМОЮ змонтованою файловою системою. Якщо
 * /sysroot — просто порожній каталог у пам'яті, значить сховище не зібралося
 * (не знайшовся диск, не відкрився LUKS, не піднявся LVM), і переходити
 * нікуди: точка монтування відрізняється від каталогу номером пристрою. */
static int newroot_is_separate_fs(const char *newroot)
{
	struct stat old_st, new_st;

	if (stat("/", &old_st) != 0) {
		boot_errno("stat", "/");
		return 0;
	}
	if (stat(newroot, &new_st) != 0) {
		boot_errno("stat", newroot);
		return 0;
	}
	if (!S_ISDIR(new_st.st_mode)) {
		boot_err("%s не є каталогом", newroot);
		return 0;
	}
	if (new_st.st_dev == old_st.st_dev) {
		boot_err("%s лежить на тій самій ФС, що й старий корінь — "
			 "справжнє сховище не змонтоване", newroot);
		return 0;
	}
	return 1;
}

/* Провідні '/' відкидаємо: після chroot init усе одно шукається від нового
 * кореня, а тут нам треба скласти шлях до перевірки ДО переходу. */
static const char *strip_slashes(const char *path)
{
	return path + strspn(path, "/");
}

/* Якщо init незапускний, дізнатися про це після execve вже пізно: процес
 * лишиться в новому корені без коду, який мав його продовжити. */
static int init_is_runnable(const char *newroot, const char *init)
{
	char path[PATH_MAX];
	int n;

	n = snprintf(path, sizeof path, "%s/%s", newroot, strip_slashes(init));
	if (n < 0 || (size_t)n >= sizeof path) {
		boot_err("шлях до init задовгий");
		return 0;
	}
	if (access(path, X_OK) != 0) {
		boot_err("%s не запускається: %s", path, strerror(errno));
		return 0;
	}
	return 1;
}

int ensure_can_switch(const char *newroot, const char *init)
{
	if (getpid() != 1) {
		boot_err("мусить виконуватися процесом PID 1, а не %d",
			 (int)getpid());
		return -1;
	}
	/* Порожній рядок і "/" зробили б із наступних кроків стирання живої
	 * системи замість переходу. */
	if (newroot[0] == '\0' || strcmp(newroot, "/") == 0) {
		boot_err("новий корінь \"%s\" не має сенсу", newroot);
		return -1;
	}
	if (!root_lives_in_memory())
		return -1;
	if (!newroot_is_separate_fs(newroot))
		return -1;
	if (!init_is_runnable(newroot, init))
		return -1;

	return 0;
}
