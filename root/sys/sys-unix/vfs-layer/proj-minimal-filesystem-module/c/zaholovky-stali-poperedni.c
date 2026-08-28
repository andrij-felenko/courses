// SPDX-License-Identifier: GPL-2.0
/* tinyfs — найменша файлова система, яку можна змонтувати */

#include <linux/module.h>
#include <linux/fs.h>
#include <linux/fs_context.h>
#include <linux/pagemap.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/timekeeping.h>

#define TINY_MAGIC	0x54494E59UL	/* "TINY" у ASCII */
#define TINY_NAME	"status"
#define TINY_BUFSZ	256

#define TINY_INO_ROOT	1
#define TINY_INO_FILE	2

static const struct inode_operations tiny_dir_inode_ops;
static const struct file_operations  tiny_dir_ops;
static const struct file_operations  tiny_file_ops;

static atomic_t tiny_opens = ATOMIC_INIT(0);
