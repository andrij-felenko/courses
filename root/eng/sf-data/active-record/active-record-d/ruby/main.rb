# Уся модель. Полів не оголошено — Active Record прочитає їх зі схеми таблиці orders.
class Order < ApplicationRecord
  belongs_to :customer

  # єдине, що тут написали руками, — предметне правило
  def can_cancel?
    %w[new paid].include?(status)
  end
end

order = Order.find(42)
if order.can_cancel?
  order.status = "cancelled"
  order.save!
end
