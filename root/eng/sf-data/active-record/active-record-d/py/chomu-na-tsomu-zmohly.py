# Поля оголошено в класі — схему таблиці Django згенерує з них міграцією.
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=16, default="new")

    # єдине, що тут написали руками, — предметне правило
    def can_cancel(self) -> bool:
        return self.status in ("new", "paid")


order = Order.objects.get(pk=42)
if order.can_cancel():
    order.status = "cancelled"
    order.save()
