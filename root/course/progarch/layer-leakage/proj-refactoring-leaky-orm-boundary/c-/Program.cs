using DigitalHomes.Contracts;
using DigitalHomes.Entities;
using DigitalHomes.Persistence;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Додаємо підтримку контролерів із налаштуванням ігнорування циклічних посилань для демонстрації Leaky-контролера
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        // Необхідно для демонстрації роботи лінивого завантаження у LeakyRoomsController:
        // інакше серіалізатор впаде через циклічні посилання RoomEntity -> DeviceEntity -> RoomEntity
        options.JsonSerializerOptions.ReferenceHandler = System.Text.Json.Serialization.ReferenceHandler.IgnoreCycles;
    });

// Реєструємо базу даних у пам'яті з увімкненими проксі для лінивого завантаження (Lazy Loading Proxies).
// Це дозволяє наочно продемонструвати витік шару в LeakyRoomsController та безпечну роботу в CleanRoomsController.
builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseInMemoryDatabase("DigitalHomesDb")
           .UseLazyLoadingProxies();
});

// Реєструємо репозиторій для чистої архітектури
builder.Services.AddScoped<IRoomRepository, RoomRepository>();

var app = builder.Build();

// Наповнюємо базу початковими тестовими даними для наочності роботи обох контролерів
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    SeedData(context);
}

app.UseRouting();
app.MapControllers();

app.Run();

// Допоміжний метод наповнення початковими даними
static void SeedData(AppDbContext context)
{
    if (context.Rooms.Any()) return;

    var livingRoom = new RoomEntity
    {
        Id = 1,
        Name = "Вітальня",
        TargetTemperature = 22.5,
        TargetHumidity = 45.0,
        Devices = new List<DeviceEntity>
        {
            new() { Id = 101, RoomId = 1, Type = "Thermostat", SerialNumber = "TH-001", IsActive = true },
            new() { Id = 102, RoomId = 1, Type = "AirQualitySensor", SerialNumber = "AQ-991", IsActive = true }
        }
    };

    var bedroom = new RoomEntity
    {
        Id = 2,
        Name = "Спальня",
        TargetTemperature = 20.0,
        TargetHumidity = 50.0,
        Devices = new List<DeviceEntity>
        {
            new() { Id = 201, RoomId = 2, Type = "Humidifier", SerialNumber = "HM-404", IsActive = false }
        }
    };

    context.Rooms.AddRange(livingRoom, bedroom);
    context.SaveChanges();
}
