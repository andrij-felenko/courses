using DigitalHomes.Entities;
using Microsoft.EntityFrameworkCore;

namespace DigitalHomes.Persistence;

/// <summary>
/// Контекст сесії Entity Framework Core.
/// Керує підключенням до сховища та життєвим циклом об'єктів у пам'яті (Change Tracker).
/// </summary>
public class AppDbContext : DbContext
{
    public DbSet<RoomEntity> Rooms => Set<RoomEntity>();
    public DbSet<DeviceEntity> Devices => Set<DeviceEntity>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Налаштування зв'язку "один-до-багатьох" між кімнатою та пристроями
        modelBuilder.Entity<RoomEntity>(entity =>
        {
            entity.HasKey(r => r.Id);
            entity.Property(r => r.Name).IsRequired().HasMaxLength(100);

            entity.HasMany(r => r.Devices)
                  .WithOne(d => d.Room)
                  .HasForeignKey(d => d.RoomId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<DeviceEntity>(entity =>
        {
            entity.HasKey(d => d.Id);
            entity.Property(d => d.Type).IsRequired().HasMaxLength(50);
            entity.Property(d => d.SerialNumber).IsRequired().HasMaxLength(100);
        });
    }
}
