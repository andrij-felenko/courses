static void acme_engine_stop(void *data)
{
	struct acme *a = data;

	writel(0, a->regs + ACME_CTRL);
}

	/* ... у probe(), після відображення регістрів ... */
	writel(ACME_CTRL_RUN, a->regs + ACME_CTRL);

	ret = devm_add_action_or_reset(dev, acme_engine_stop, a);
	if (ret)
		return ret;
