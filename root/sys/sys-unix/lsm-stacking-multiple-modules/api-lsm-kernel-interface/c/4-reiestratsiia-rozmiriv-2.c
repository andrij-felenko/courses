static void __init lsm_set_blob_size(int *need, int *lbs)
{
	int offset;

	if (*need <= 0)
		return;
	offset = ALIGN(*lbs, sizeof(void *));	/* вирівнювання під покажчик */
	*lbs = offset + *need;			/* нова сума розмірів */
	*need = offset;				/* модулю лишається зміщення */
}
