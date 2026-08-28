static inline u32 readl(const volatile void __iomem *addr)
{
        u32 val;
        __io_br();                                          /* бар'єр до доступу */
        val = __le32_to_cpu((__le32 __force)__raw_readl(addr));
        __io_ar(val);                                       /* бар'єр після доступу */
        return val;
}

static inline void writel(u32 value, volatile void __iomem *addr)
{
        __io_bw();                                          /* бар'єр до доступу */
        __raw_writel((u32 __force)__cpu_to_le32(value), addr);
        __io_aw();
}
