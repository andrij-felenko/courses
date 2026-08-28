// Пряма прив'язка: доменний сервіс знає про тип AWS DynamoDB Client
import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";

export class SensorService {
  constructor(private db: DynamoDBClient) {}

  async saveTelemetry(sensorId: string, temp: number) {
    // Proprietary формат даних {"S": ...}, {"N": ...} протекти в бізнес-код
    await this.db.send(new PutItemCommand({
      TableName: "Telemetry",
      Item: {
        SensorId: { S: sensorId },
        Temperature: { N: temp.toString() },
        Timestamp: { N: Date.now().toString() }
      }
    }));
  }
}
