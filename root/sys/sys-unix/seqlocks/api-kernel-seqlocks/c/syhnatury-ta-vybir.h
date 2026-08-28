/* Стандартне блокування у контексті процесу (без вимкнення переривань) */
void write_seqlock(seqlock_t *sl);
void write_sequnlock(seqlock_t *sl);

/* Блокування зі збереженням прапорців переривань (IRQ-safe) */
void write_seqlock_irqsave(seqlock_t *sl, unsigned long flags);
void write_sequnlock_irqrestore(seqlock_t *sl, unsigned long flags);

/* Блокування з вимкненням нижніх половин (SoftIRQ-safe) */
void write_seqlock_bh(seqlock_t *sl);
void write_sequnlock_bh(seqlock_t *sl);

/* Блокування з вимкненням апаратних переривань на поточному ядрі */
void write_seqlock_irq(seqlock_t *sl);
void write_sequnlock_irq(seqlock_t *sl);
