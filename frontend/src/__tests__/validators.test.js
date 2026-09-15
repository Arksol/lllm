import { describe, expect, it } from "vitest";
import { validateRepoUrl } from "../utils/validators";

describe("validateRepoUrl", () => {
  it("acepta una url de github", () => {
    expect(validateRepoUrl("https://github.com/psf/requests")).toBeNull();
  });

  it("acepta una url sin esquema", () => {
    expect(validateRepoUrl("github.com/psf/requests")).toBeNull();
  });

  it("acepta hugging face con prefijo de tipo", () => {
    expect(validateRepoUrl("https://huggingface.co/datasets/org/corpus")).toBeNull();
  });

  it("rechaza un dominio no permitido", () => {
    expect(validateRepoUrl("https://ejemplo.com/a/b")).toMatch(/solo se admiten/i);
  });

  it("rechaza una url incompleta", () => {
    expect(validateRepoUrl("https://github.com/psf")).toMatch(/falta/i);
  });

  it("rechaza el campo vacio", () => {
    expect(validateRepoUrl("")).toMatch(/escribe/i);
  });
});
