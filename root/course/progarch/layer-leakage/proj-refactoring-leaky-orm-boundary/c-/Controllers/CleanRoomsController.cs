using DigitalHomes.Contracts;
using DigitalHomes.Persistence;
using Microsoft.AspNetCore.Mvc;

namespace DigitalHomes.Controllers;

/// <summary>
/// ВІДРЕФАКТОРЕНИЙ КОНТРОЛЕР: Архітектурну межу відновлено.
/// Веб-рівень спілкується зі сховищем суто через абстракцію IRoomRepository та стабільні DTO.
/// Контролер не знає про існування EF Core, Lazy Loading або структур таблиць БД.
/// </summary>
[ApiController]
[Route("api/clean/rooms")]
public class CleanRoomsController : ControllerBase
{
    private readonly IRoomRepository _repository;

    public CleanRoomsController(IRoomRepository repository)
    {
        _repository = repository;
    }

    /// <summary>
    /// Отримання всіх кімнат: дані вже вичитані з бази в пам'ять як колекція DTO.
    /// Під час формування JSON-відповіді жодних додаткових звернень до БД не відбувається.
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IReadOnlyList<RoomResponseDto>>> GetAllRooms(CancellationToken ct)
    {
        var rooms = await _repository.GetAllRoomsAsync(ct);
        return Ok(rooms);
    }

    /// <summary>
    /// Отримання кімнати за ідентифікатором: контракт повністю ізольований від моделі бази.
    /// </summary>
    [HttpGet("{id:int}")]
    public async Task<ActionResult<RoomResponseDto>> GetRoomById(int id, CancellationToken ct)
    {
        var room = await _repository.GetRoomByIdAsync(id, ct);
        if (room == null)
        {
            return NotFound($"Кімнату з ідентифікатором {id} не знайдено.");
        }

        return Ok(room);
    }

    /// <summary>
    /// Оновлення параметрів клімату: приймає строго типізовану команду.
    /// Запобігає масовому призначенню, обробляє доменні помилки та повертає статусний код.
    /// </summary>
    [HttpPut("{id:int}/climate")]
    public async Task<IActionResult> UpdateClimate(
        int id,
        [FromBody] UpdateRoomClimateCommand command,
        CancellationToken ct)
    {
        try
        {
            var updated = await _repository.UpdateClimateAsync(id, command, ct);
            if (!updated)
            {
                return NotFound($"Кімнату з ідентифікатором {id} не знайдено.");
            }

            return NoContent();
        }
        catch (ArgumentOutOfRangeException ex)
        {
            // Помилки валідації повертаються як коректний HTTP 400 Bad Request замість аварійного 500
            return BadRequest(new { error = ex.Message });
        }
    }
}
