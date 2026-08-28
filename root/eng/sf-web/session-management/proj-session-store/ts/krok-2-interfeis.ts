export interface Session {
  userId: string;
  createdAt: number;                              // мс, початок абсолютного строку
}

export interface Store {
  create(userId: string): Promise<string>;        // → новий sid
  lookup(sid: string): Promise<Session | null>;   // null — немає/згасла; усередині ковзає idle
  rotate(sid: string): Promise<string | null>;    // новий номер, ті самі дані, старий мертвий
  destroy(sid: string): Promise<void>;
}
