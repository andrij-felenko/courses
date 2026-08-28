/* Дев'ять значущих бітів вирівняні вліво, крок — пів градуса.
   Тип ОБОВ'ЯЗКОВО знаковий: інакше зсув затягне нулі замість знака. */
static long ms_reg_to_mc(s16 reg)
{
        return (reg >> 7) * 500;
}

static u16 ms_mc_to_reg(long mc)
{
        mc = clamp_val(mc, -55000, 125000);
        return (u16)(s16)(DIV_ROUND_CLOSEST(mc, 500) * 128);
}
