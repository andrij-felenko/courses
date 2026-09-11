using DigitalHomes.Entities;
using DigitalHomes.Persistence;
using Microsoft.AspNetCore.Mvc;

namespace DigitalHomes.Controllers;

/// <summary>
/// АНТИПАТЕРН: Контролер із витоком деталей реалізації шару персистентності.
/// Демонструє типові архітектурні вади: експорт IQueryable, неконтрольоване ліниве завантаження,
/// розмивання меж транзакцій та пряме використання сутностей бази замість контрактів API.
/// </summary>
[ApiController]
[Route("api/leaky/rooms")]
public class LeakyRoomsController : ControllerBase
{
    private readonly AppDbContext _context;

    // ПРЯМА ЗАЛЕЖНІСТЬ: Контролер напряму прив'язаний до контексту EF Core,
    // минаючи доменний шар чи сервісну межу.
    public LeakyRoomsController(AppDbContext context)
    {
        _context = context;
    }

    /// <summary>
    /// ВИТІК 1: Повернення IQueryable безпосередньо з контролера.
    /// Запит до сховища не виконується тут. Виконання відкладається до моменту JSON-серіалізації.
    /// Якщо підключено Lazy Loading, звернення серіалізатора до RoomEntity.Devices згенерує
    /// додатковий SQL-запит для кожної кімнати (катастрофічна проблема N+1).
    /// </summary>
    [HttpGet]
    public IQueryable<RoomEntity> GetRooms()
    {
        // Клієнт API або презентаційний конвеєр отримує контроль над запитом.
        // Сесія з'єднання з БД лишається відкритою аж до завершення передачі HTTP-пакета.
        return _context.Rooms;
    }

    /// <summary>
    /// ВИТІК 2: Віддача внутрішньої ORM-сутності назовні.
    /// Публічний контракт жорстко зв'язується зі схемою таблиці в БД.
    /// Будь-яке нове поле в базі автоматично потрапляє в API, порушуючи інкапсуляцію.
    /// </summary>
    [HttpGet("{id:int}")]
    public ActionResult<RoomEntity> GetRoom(int id)
    {
        var room = _context.Rooms.Find(id);
        if (room == null)
        {
            return NotFound($"Кімнату з ідентифікатором {id} не знайдено.");
        }

        // Сесія DbContext залишається активною. Під час серіалізації виклик геттера Devices
        // виконає прихований синхронний/асинхронний мережевий запит до БД поза межами контролера.
        return room;
    }

    /// <summary>
    /// ВИТІК 3: Mass Assignment (Over-posting) через прив'язку тіла запиту до сутності БД.
    /// Зловмисник може надіслати підроблені поля Id чи змінити Devices без жодної бізнес-валідації.
    /// </summary>
    [HttpPut("{id:int}/climate")]
    public IActionResult UpdateClimate(int id, [FromBody] RoomEntity payload)
    {
        var room = _context.Rooms.Find(id);
        if (room == null)
        {
            return NotFound($"Кімнату з ідентифікатором {id} не знайдено.");
        }

        // Відсутня перевірка допустимих меж параметрів (наприклад, чи реалістична температура 120°C).
        room.TargetTemperature = payload.TargetTemperature;
        room.TargetHumidity = payload.TargetHumidity;

        // Збереження викликається прямо у веб-обробнику. Якщо виникне помилка,
        // клієнт отримає технічний виняток ORM замість зрозумілої бізнес-помилки.
        _context.SaveChanges();

        return NoContent();
    }
}
