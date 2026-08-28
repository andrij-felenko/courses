// Змінити місто в адресі клієнта в замовленні — а все незмінне:
const updated = {
  ...order,
  customer: {
    ...order.customer,
    address: {
      ...order.customer.address,
      city: "Львів",             // одна змістовна зміна...
    },
  },
};                               // ...а переписати руками довелося весь ланцюг до неї
