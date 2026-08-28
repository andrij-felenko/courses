struct sock_filter filter[] = {
	/* 0 */ BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
			 offsetof(struct seccomp_data, arch)),
	/* 1 */ BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
	/* 2 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

	/* 3 */ BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
			 offsetof(struct seccomp_data, nr)),
	/* 4 */ BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, __X32_SYSCALL_BIT, 0, 1),
	/* 5 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

	/* 6 */ /* лише тут можна порівнювати самі номери викликів */
	        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
};
