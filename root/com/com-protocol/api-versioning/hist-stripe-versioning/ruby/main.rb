# Модуль знає лише, як ВІДКОТИТИ нову форму назад до старої.
class CollapseEventRequest < AbstractVersionChange
  description "Поле `request` тепер об'єкт (id + ключ ідемпотентності), " \
              "а не голий рядок-ідентифікатор."

  response EventAPIResource do
    change :request, type_old: String, type_new: Hash

    # Для клієнта, пришпиленого ДО цієї зміни, згортаємо об'єкт назад у рядок:
    run do |data|
      data.merge(request: data[:request][:id])
    end
  end
end
