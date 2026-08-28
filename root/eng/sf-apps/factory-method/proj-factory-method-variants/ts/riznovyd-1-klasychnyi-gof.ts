abstract class ProfileImporter {
  // фабричний метод: каркас НЕ знає конкретного парсера, лишає діру
  protected abstract createParser(): ProfileParser;

  // спільний процес — той самий для всіх форматів
  import(raw: string): Profile {
    const parser = this.createParser();   // ...кличе діру...
    const profile = parser.parse(raw);
    this.assertRequiredFields(profile);
    this.log(`Імпортовано ${profile.email}`);
    return profile;
  }

  private assertRequiredFields(p: Profile): void {
    if (!p.email) throw new Error("Профіль без email");
  }
  private log(msg: string): void { /* ... */ }
}

class JsonProfileImporter extends ProfileImporter {
  protected createParser(): ProfileParser {   // нащадок ОБИРАЄ клас
    return new JsonProfileParser();
  }
}
class CsvProfileImporter extends ProfileImporter {
  protected createParser(): ProfileParser {
    return new CsvProfileParser();
  }
}
