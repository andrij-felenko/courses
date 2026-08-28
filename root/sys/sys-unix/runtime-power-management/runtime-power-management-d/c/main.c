static int mydev_runtime_suspend(struct device *dev)
{
    struct mydev *d = dev_get_drvdata(dev);

    if (mydev_busy(d))          /* встигли зайняти, доки ми йшли сюди */
        return -EBUSY;

    mydev_save_context(d);      /* зберегти те, що зникне разом із живленням */
    clk_disable_unprepare(d->clk);
    regulator_disable(d->vdd);
    return 0;
}

static int mydev_runtime_resume(struct device *dev)
{
    struct mydev *d = dev_get_drvdata(dev);
    int ret;

    ret = regulator_enable(d->vdd);
    if (ret)
        return ret;
    ret = clk_prepare_enable(d->clk);
    if (ret) {
        regulator_disable(d->vdd);
        return ret;
    }
    mydev_restore_context(d);   /* повернути регістри, які втратили живлення */
    return 0;
}

static const struct dev_pm_ops mydev_pm_ops = {
    RUNTIME_PM_OPS(mydev_runtime_suspend, mydev_runtime_resume, NULL)
};
