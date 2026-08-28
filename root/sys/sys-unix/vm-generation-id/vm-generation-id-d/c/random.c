/* drivers/char/random.c */
void __cold add_vmfork_randomness(const void *unique_vm_id, size_t len)
{
	add_device_randomness(unique_vm_id, len);
	if (crng_ready()) {
		crng_reseed(NULL);
		pr_notice("crng reseeded due to virtual machine fork\n");
	}
	blocking_notifier_call_chain(&vmfork_chain, 0, NULL);
}
