// ArchUnit / Static Analysis Fitness Test
import { ArchRuleBuilder } from "@archunit/core";

describe("Architecture Boundary & Migration Fitness Tests", () => {
  it("BFF modules MUST NOT access Legacy Twin B directly", async () => {
    const rule = ArchRuleBuilder.classes()
      .that()
      .resideInAPackage("..bff..")
      .should()
      .onlyDependOnClassesThat()
      .resideInAnyPackage("..facade..", "..dto..", "java..");

    await rule.check();
  });

  it("All Twin state mutations MUST generate Outbox events", async () => {
    const mutationMethods = findAnnotatedMethods("@TwinMutation");
    for (const method of mutationMethods) {
      expect(method.hasOutboxTransaction()).toBe(true);
    }
  });
});
