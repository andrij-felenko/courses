// TypeScript / Node.js: gRPC Client Config з передачею metadata home_id
import * as grpc from '@grpc/grpc-js';

export function createIngestClient(target: string, homeId: string): grpc.Client {
  const options: grpc.ClientOptions = {
    'grpc.keepalive_time_ms': 30000,
    'grpc.keepalive_timeout_ms': 10000,
    'grpc.keepalive_permit_without_calls': 1,
  };

  const client = new grpc.Client(target, grpc.credentials.createInsecure(), options);
  
  // Додаємо x-home-id у метадані виклику за замовчуванням
  const metadata = new grpc.Metadata();
  metadata.add('x-home-id', homeId);

  return client;
}
