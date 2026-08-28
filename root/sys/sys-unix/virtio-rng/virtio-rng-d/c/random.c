/* drivers/char/random.c */
void add_hwgenerator_randomness(const void *buf, size_t len, size_t entropy,
				bool sleep_after)
{
	mix_pool_bytes(buf, len);
	credit_init_bits(entropy);

	if (sleep_after && !kthread_should_stop() && (crng_ready() || !entropy))
		schedule_timeout_interruptible(crng_reseed_interval());
}
