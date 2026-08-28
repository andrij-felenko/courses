// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/notifier.h>
#include <linux/random.h>
#include <linux/mutex.h>
#include <linux/string.h>

/* Сеансовий стан, який після роздвоєння вживати вже не можна. */
static DEFINE_MUTEX(session_lock);
static u8  session_key[32];
static u64 session_nonce;
static u64 session_epoch;      /* міняється лише під session_lock */

static void session_rekey(void)
{
	get_random_bytes(session_key, sizeof(session_key));
	session_nonce = 0;
	WRITE_ONCE(session_epoch, session_epoch + 1);
}

static int vmfork_react(struct notifier_block *nb, unsigned long action, void *data)
{
	/* Ланцюжок блокувальний: спати й брати м'ютекси тут можна. */
	mutex_lock(&session_lock);
	session_rekey();
	mutex_unlock(&session_lock);

	pr_notice("vmfork-demo: session state discarded after VM fork\n");
	return NOTIFY_DONE;
}

static struct notifier_block vmfork_nb = { .notifier_call = vmfork_react };

/* Видача одноразового числа, яка вміє помітити роздвоєння посеред себе.
 * Оголошення — у вашому заголовку, звідти її кличе решта коду.
 */
int session_take_nonce(u8 key_out[32], u64 *nonce_out)
{
	u64 epoch;

	mutex_lock(&session_lock);
	epoch = session_epoch;
	memcpy(key_out, session_key, sizeof(session_key));
	*nonce_out = session_nonce++;
	mutex_unlock(&session_lock);

	/* Якщо роздвоєння сталося саме зараз — пара застаріла, викидаємо її. */
	return READ_ONCE(session_epoch) == epoch ? 0 : -EAGAIN;
}

static int __init vmfork_demo_init(void)
{
	if (!IS_ENABLED(CONFIG_VMGENID)) {
		pr_warn("vmfork-demo: kernel built without CONFIG_VMGENID\n");
		return -ENODEV;
	}
	mutex_lock(&session_lock);
	session_rekey();
	mutex_unlock(&session_lock);
	return register_random_vmfork_notifier(&vmfork_nb);
}

static void __exit vmfork_demo_exit(void)
{
	unregister_random_vmfork_notifier(&vmfork_nb);
	memzero_explicit(session_key, sizeof(session_key));
}

module_init(vmfork_demo_init);
module_exit(vmfork_demo_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Скидання сеансового стану після клонування машини");
