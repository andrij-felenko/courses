/* switch_root — останній крок initramfs.
 *
 * Робимо підготовлений /sysroot справжнім коренем і замінюємо код процесу
 * на /sbin/init, НЕ створюючи нового процесу: номер 1 лишається за нами.
 * Порядок тут той самий, що у фазі 5: перевірити · зняти спільне поширення
 * монтувань · перенести службові дерева · стерти тимчасову rootfs ·
 * переставити корінь · перевідкрити консоль · викликати execv.
 *
 * Збірка:  cc -Wall -Wextra -O2 -o switch_root \
 *              main.c checks.c mounts.c wipe.c console.c log.c
 * Виклик:  switch_root /sysroot /sbin/init
 */

#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/mount.h>
#include <unistd.h>

#include "log.h"
#include "steps.h"

int main(int argc, char **argv)
{
	const char *newroot;
	const char *init;
	unsigned long failed;
	int rootfd;

	if (argc < 3) {
		fprintf(stderr, "вжиток: %s <новий-корінь> <init> [аргументи init…]\n",
			argv[0] ? argv[0] : "switch_root");
		return 2;
	}
	newroot = argv[1];
	init = argv[2];

	/* Крок 0: усе, що ще можна перевірити без незворотних дій. */
	if (ensure_can_switch(newroot, init) != 0)
		return 1;

	/* Крок 1: службові дерева переїжджають у новий корінь. Спершу знімаємо
	 * спільне поширення — інакше перший же MS_MOVE відмовить з EINVAL. */
	if (make_mount_tree_private() != 0)
		return 1;

	failed = move_special_mounts(newroot);
	if (failed != 0)
		boot_err("не перенесено монтувань: %lu", failed);

	/* Переходимо в новий корінь ДО стирання: поточний каталог процесу не має
	 * зникнути разом зі старою ФС, та й "." нижче стане джерелом для MS_MOVE. */
	if (chdir(newroot) != 0) {
		boot_errno("chdir", newroot);
		return 1;
	}

	/* Крок 2: стираємо тимчасову rootfs і повертаємо її сторінки ядру.
	 * Дескриптор старого кореня беремо ДО chroot: після нього шляху туди
	 * вже не буде, а chdir нас звідти щойно вивів. */
	rootfd = open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC);
	if (rootfd < 0) {
		boot_errno("open", "/");
		return 1;
	}
	failed = wipe_filesystem(rootfd);
	close(rootfd);
	if (failed != 0)
		boot_err("не стерто записів: %lu", failed);

	/* Крок 3: підміна кореневого вузла простору імен монтувань.
	 * pivot_root() тут повернув би EINVAL — rootfs є первинним коренем. */
	if (mount(".", "/", NULL, MS_MOVE, NULL) != 0) {
		boot_errno("mount(\".\", \"/\", MS_MOVE)", NULL);
		return 1;
	}
	if (chroot(".") != 0) {
		boot_errno("chroot", ".");
		return 1;
	}
	if (chdir("/") != 0) {
		boot_errno("chdir", "/");
		return 1;
	}

	/* Крок 4: консоль нового кореня на дескрипторах 0, 1, 2. Вони переживуть
	 * execve, тому системний менеджер успадкує саме її. */
	reopen_console();

	/* Крок 5: заміна коду процесу. Ні fork, ні posix_spawn: номер 1 має
	 * лишитися за цим самим процесом, а не перейти до нащадка. */
	execv(init, argv + 2);

	boot_errno("execv", init);
	/* Відступати нікуди: щойно PID 1 завершиться, ядро впаде в паніку. */
	return 1;
}
