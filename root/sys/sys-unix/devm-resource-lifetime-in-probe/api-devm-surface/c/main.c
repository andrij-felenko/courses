struct acme_gate {
	void __iomem	*ctrl;
};

static void acme_gate_release(struct device *dev, void *res)
{
	struct acme_gate *g = res;

	writel(0, g->ctrl);
}

static int acme_gate_open(struct device *dev, void __iomem *ctrl)
{
	struct acme_gate *g;

	g = devres_alloc(acme_gate_release, sizeof(*g), GFP_KERNEL);
	if (!g)
		return -ENOMEM;

	g->ctrl = ctrl;
	writel(ACME_GATE_ON, ctrl);
	devres_add(dev, g);	/* з цієї миті звільнення гарантоване */
	return 0;
}
