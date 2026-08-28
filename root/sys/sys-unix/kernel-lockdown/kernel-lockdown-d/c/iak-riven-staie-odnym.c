/* include/linux/security.h — порядок значень тут і є політикою */
enum lockdown_reason {
	LOCKDOWN_NONE,
	LOCKDOWN_MODULE_SIGNATURE,
	LOCKDOWN_DEV_MEM,
	LOCKDOWN_KEXEC,
	LOCKDOWN_HIBERNATION,
	/* … ще півтора десятка причин запису … */
	LOCKDOWN_INTEGRITY_MAX,
	LOCKDOWN_KCORE,
	LOCKDOWN_KPROBES,
	LOCKDOWN_PERF,
	LOCKDOWN_TRACEFS,
	/* … */
	LOCKDOWN_CONFIDENTIALITY_MAX,
};
