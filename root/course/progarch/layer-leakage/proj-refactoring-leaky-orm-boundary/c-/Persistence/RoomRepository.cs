using DigitalHomes.Contracts;
using DigitalHomes.Entities;
using Microsoft.EntityFrameworkCore;

namespace DigitalHomes.Persistence;

/// <summary>
/// Контракт репозиторію кімнат, що проводить чітку межу між бізнес-логікою і збереженням.
/// Жоден метод не повертає IQueryable чи сутності ORM за межі цього інтерфейсу.
/// </summary>
public interface IRoomRepository
{
    Task<IReadOnlyList<RoomResponseDto>> GetAllRoomsAsync(CancellationToken ct = default);
    Task<RoomResponseDto?> GetRoomByIdAsync(int id, CancellationToken ct = default);
    Task<bool> UpdateClimateAsync(int id, UpdateRoomClimateCommand command, CancellationToken ct = default);
}

/// <summary>
/// Реалізація репозиторію на основі EF Core.
/// Інкапсулює роботу з DbContext: використовує проєкції Select для швидкого читання без трекінгу
/// та випереджальне завантаження (Include) для команд модифікації агрегату.
/// </summary>
public class RoomRepository : IRoomRepository
{
    private readonly AppDbContext _context;

    public RoomRepository(AppDbContext context)
    {
        _context = context;
    }

    /// <summary>
    /// ЧИТАННЯ: Явна проєкція на рівні SQL через Select.
    /// EF Core транслює цей вираз в один оптимізований SQL-запит із JOIN.
    /// AsNoTracking() вимикає механізм відстеження змін у пам'яті, заощаджуючи ресурси процесора та RAM.
    /// Lazy loading не викликається, проблема N+1 відсутня за визначенням.
    /// </summary>
    public async Task<IReadOnlyList<RoomResponseDto>> GetAllRoomsAsync(CancellationToken ct = default)
    {
        return await _context.Rooms
            .AsNoTracking()
            .Select(r => new RoomResponseDto(
                r.Id,
                r.Name,
                r.TargetTemperature,
                r.TargetHumidity,
                r.Devices.Select(d => new DeviceDto(
                    d.Id,
                    d.Type,
                    d.SerialNumber,
                    d.IsActive
                )).ToList()
            ))
            .ToListAsync(ct);
    }

    /// <summary>
    /// ЧИТАННЯ ОДИНИЧНОГО ОБ'ЄКТА: Проєкція повертає готовий DTO, сесія звільняється негайно.
    /// </summary>
    public async Task<RoomResponseDto?> GetRoomByIdAsync(int id, CancellationToken ct = default)
    {
        return await _context.Rooms
            .AsNoTracking()
            .Where(r => r.Id == id)
            .Select(r => new RoomResponseDto(
                r.Id,
                r.Name,
                r.TargetTemperature,
                r.TargetHumidity,
                r.Devices.Select(d => new DeviceDto(
                    d.Id,
                    d.Type,
                    d.SerialNumber,
                    d.IsActive
                )).ToList()
            ))
            .FirstOrDefaultAsync(ct);
    }

    /// <summary>
    /// МОДИФІКАЦІЯ СТАНУ: Випереджальне завантаження через Include гарантує цілісність агрегату.
    /// Транзакційна сесія відкривається, валідується та атомарно фіксується всередині сховища.
    /// </summary>
    public async Task<bool> UpdateClimateAsync(int id, UpdateRoomClimateCommand command, CancellationToken ct = default)
    {
        // Валідація бізнес-інваріантів перед зверненням до персистентності
        if (command.TargetTemperature is < 10.0 or > 38.0)
        {
            throw new ArgumentOutOfRangeException(nameof(command.TargetTemperature),
                "Цільова температура має бути в межах від 10.0°C до 38.0°C.");
        }

        if (command.TargetHumidity is < 20.0 or > 85.0)
        {
            throw new ArgumentOutOfRangeException(nameof(command.TargetHumidity),
                "Цільова вологість має бути в межах від 20.0% до 85.0%.");
        }

        // Завантажуємо кімнату разом із пристроями одразу (Eager Loading), без лінивих звернень
        var room = await _context.Rooms
            .Include(r => r.Devices)
            .FirstOrDefaultAsync(r => r.Id == id, ct);

        if (room == null)
        {
            return false;
        }

        room.TargetTemperature = command.TargetTemperature;
        room.TargetHumidity = command.TargetHumidity;

        // Транзакція завершується тут, контекст закриває сесію до повернення керування у веб-шар
        await _context.SaveChangesAsync(ct);
        return true;
    }
}
