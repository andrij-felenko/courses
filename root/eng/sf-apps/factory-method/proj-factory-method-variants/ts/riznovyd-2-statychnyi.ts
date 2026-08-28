class Profile {
  // конструктор лишаємо приватним: назовні через нього не ходять
  private constructor(
    readonly email: string,
    readonly displayName: string,
    readonly verified: boolean,
  ) {}

  // осмислені входи в клас — кожен зі СВОЄЮ назвою і своїм добором
  static register(email: string, displayName: string): Profile {
    return new Profile(email.toLowerCase(), displayName, /*verified*/ false);
  }
  static fromVerifiedInvite(email: string): Profile {
    return new Profile(email.toLowerCase(), email.split("@")[0], /*verified*/ true);
  }
  static anonymous(): Profile {
    return new Profile("", "Гість", false);
  }
}

const a = Profile.register("Ann@Ex.com", "Ann");     // → verified=false
const b = Profile.fromVerifiedInvite("bob@ex.com");  // → verified=true
