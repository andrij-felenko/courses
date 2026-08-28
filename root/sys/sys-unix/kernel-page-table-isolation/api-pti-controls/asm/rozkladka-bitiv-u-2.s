.macro SWITCH_TO_USER_CR3 scratch_reg:req scratch_reg2:req
	mov	%cr3, \scratch_reg
	ALTERNATIVE "jmp .Lwrcr3_\@", "", X86_FEATURE_PCID
	movq	\scratch_reg, \scratch_reg2
	andq	$(0x7FF), \scratch_reg
	bt	\scratch_reg, THIS_CPU_user_pcid_flush_mask
	jnc	.Lnoflush_\@
	btr	\scratch_reg, THIS_CPU_user_pcid_flush_mask
	movq	\scratch_reg2, \scratch_reg
	jmp	.Lwrcr3_pcid_\@
.Lnoflush_\@:
	movq	\scratch_reg2, \scratch_reg
	SET_NOFLUSH_BIT \scratch_reg
.Lwrcr3_pcid_\@:
	orq	$(PTI_USER_PCID_MASK), \scratch_reg
.Lwrcr3_\@:
	orq     $(PTI_USER_PGTABLE_MASK), \scratch_reg
	mov	\scratch_reg, %cr3
.endm
