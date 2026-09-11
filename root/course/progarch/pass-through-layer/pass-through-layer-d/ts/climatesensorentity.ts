// ClimateSensorEntity.ts
@Entity({ name: 'climate_sensors' })
export class ClimateSensorEntity {
  @PrimaryColumn('uuid')
  id: string;

  @Column('float')
  temperature: number;

  @Column('float')
  humidity: number;

  @Column({ name: 'battery_level', type: 'smallint' })
  batteryLevel: number;
}
