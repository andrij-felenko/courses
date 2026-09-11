// Зовнішній DTO: пухкий сирий простір станів
type RegisterUserDto = {
  email: string;
  age: number;
};

// Доменна сутність: поля захищені приватними конструкторами або номінальними типами
type Email = { readonly __brand: unique symbol; value: string };
type Age = { readonly __brand: unique symbol; value: number };

type UserEntity = {
  email: Email;
  age: Age;
};

// Тип-сума можливих порушень інваріантів
type DomainError =
  | { kind: "InvalidEmailFormat"; input: string }
  | { kind: "AgeOutOfBounds"; input: number };

type Result<T, E> =
  | { success: true; data: T }
  | { success: false; error: E };

// Тотальний морфізм: g: RegisterUserDto -> UserEntity + DomainError
function mapDtoToUser(dto: RegisterUserDto): Result<UserEntity, DomainError> {
  if (!dto.email.includes("@") || dto.email.trim().length < 3) {
    return {
      success: false,
      error: { kind: "InvalidEmailFormat", input: dto.email }
    };
  }

  if (dto.age < 18 || dto.age > 120) {
    return {
      success: false,
      error: { kind: "AgeOutOfBounds", input: dto.age }
    };
  }

  return {
    success: true,
    data: {
      email: dto.email as unknown as Email,
      age: dto.age as unknown as Age
    }
  };
}
