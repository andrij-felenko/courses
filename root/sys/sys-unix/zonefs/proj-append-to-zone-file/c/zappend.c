/* zappend.c — дописування у файл послідовної зони zonefs.
 * збірка: cc -O2 -Wall -Wextra -o zappend zappend.c
 * запуск: sudo ./zappend /mnt/z/seq/0 /mnt/z/cnv/0
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define CHUNK (6u << 20)   /* 6 МіБ: навмисно НЕ дільник 64-мебібайтної зони */

struct zone {
	off_t  wp;    /* st_size:    вказівник запису */
	off_t  cap;   /* st_blocks:  місткість зони, вона ж найбільший розмір */
	size_t blk;   /* st_blksize: крок вирівнювання прямого запису */
};

/* Єдине джерело правди про зону — сам пристрій, перепитаний через fstat. */
static int look(int fd, struct zone *z)
{
	struct stat st;

	if (fstat(fd, &st) < 0)
		return -1;
	z->wp  = st.st_size;
	z->cap = (off_t)st.st_blocks * 512;   /* st_blocks завжди в одиницях по 512 Б */
	z->blk = (size_t)st.st_blksize;
	return 0;
}

static const char *ename(int e)
{
	switch (e) {
	case EINVAL: return "EINVAL";
	case EFBIG:  return "EFBIG";
	case EIO:    return "EIO";
	case EPERM:  return "EPERM";
	default:     return strerror(e);
	}
}

static void say(const char *what, ssize_t r)
{
	if (r < 0)
		printf("  %s → %s\n", what, ename(errno));
	else
		printf("  %s → %zd Б\n", what, r);
}

/* Окреме відкриття потрібне там, де перевіряють саме прапорці відкриття. */
static void try_write(const char *path, int flags, const void *buf, size_t len,
		      const char *what)
{
	int fd = open(path, flags);

	if (fd < 0) {
		printf("  %s → не відкрився: %s\n", what, strerror(errno));
		return;
	}
	say(what, write(fd, buf, len));
	close(fd);
}

int main(int argc, char **argv)
{
	const char *seq = argc > 1 ? argv[1] : "/mnt/z/seq/0";
	const char *cnv = argc > 2 ? argv[2] : "/mnt/z/cnv/0";
	size_t align = (size_t)sysconf(_SC_PAGESIZE);
	struct zone z;
	void *buf;
	int fd;

	/* O_DIRECT обов'язковий: буферизований запис у seq-файл не приймають узагалі. */
	fd = open(seq, O_RDWR | O_DIRECT);
	if (fd < 0 || look(fd, &z) < 0) {
		perror(seq);
		return 1;
	}
	printf("%s: вказівник %lld, місткість %lld, блок %zu\n",
	       seq, (long long)z.wp, (long long)z.cap, z.blk);

	/* Прямий запис вимагає вирівняної адреси буфера. Сторінка кратна будь-якому
	   розмірові блока, тож вирівнювання по ній не буває замалим. */
	if (posix_memalign(&buf, align, CHUNK) != 0) {
		fprintf(stderr, "немає вирівняної пам'яті\n");
		return 1;
	}
	memset(buf, 0xA5, CHUNK);

	/* Чистий старт. Це не правка обліку, а команда скидання до самого носія. */
	if (ftruncate(fd, 0) < 0)
		perror("скидання зони");

	look(fd, &z);
	say("перший дозволений запис — у самий кінець файлу",
	    pwrite(fd, buf, CHUNK, z.wp));

	puts("\nнавмисні порушення контракту:");
	look(fd, &z);
	say("запис на блок назад від кінця",
	    pwrite(fd, buf, z.blk, z.wp - (off_t)z.blk));
	say("запис у кінець, але довжиною 100 Б",
	    pwrite(fd, buf, 100, z.wp));
	say("запис за місткістю зони",
	    pwrite(fd, buf, z.blk, z.cap));
	say("читання за місткістю зони",
	    pread(fd, buf, z.blk, z.cap));
	say("читання за розміром, у межах зони",
	    pread(fd, buf, z.blk, z.wp));

	try_write(seq, O_WRONLY, buf, z.blk,                /* без O_DIRECT */
		  "буферизований запис у seq-файл");
	try_write(cnv, O_WRONLY | O_DIRECT | O_APPEND, buf, z.blk,
		  "O_APPEND у файлі звичайної зони");

	/* O_APPEND у seq-файлі: зміщення підставляє ядро під замком inode,
	   тож між «дізнатися розмір» і «записати» не лишається щілини. */
	try_write(seq, O_WRONLY | O_DIRECT | O_APPEND, buf, CHUNK,
		  "write() з O_APPEND — зміщення вибирає ядро");

	puts("\nскорочення — обидва дозволені значення й одне заборонене:");
	look(fd, &z);
	printf("  ftruncate до половини місткості → %s\n",
	       ftruncate(fd, z.cap / 2) < 0 ? ename(errno) : "прийнято");
	printf("  ftruncate до місткості (завершення зони) → %s\n",
	       ftruncate(fd, z.cap) < 0 ? ename(errno) : "прийнято");
	look(fd, &z);
	printf("  розмір завершеної зони: %lld\n", (long long)z.wp);
	say("запис у завершену зону", pwrite(fd, buf, z.blk, z.wp));
	printf("  ftruncate до нуля (скидання зони) → %s\n",
	       ftruncate(fd, 0) < 0 ? ename(errno) : "прийнято");

	puts("\nзаповнення зони до кінця:");
	while (look(fd, &z) == 0 && z.wp < z.cap) {
		ssize_t r = pwrite(fd, buf, CHUNK, z.wp);

		if (r <= 0) {
			printf("  зупинилися на %lld: %s\n", (long long)z.wp, ename(errno));
			break;
		}
		if ((size_t)r != CHUNK)
			printf("  короткий запис на зміщенні %lld: просили %u, узяли %zd\n",
			       (long long)z.wp, CHUNK, r);
	}
	look(fd, &z);
	printf("розмір наприкінці: %lld\n", (long long)z.wp);

	free(buf);
	close(fd);
	return 0;
}
