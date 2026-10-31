import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
	await page.goto("/");
});

test("adds a student, then finds them with search", async ({ page }) => {
	await page.getByPlaceholder("Digite o nome completo").fill("Lanna Correia");
	await page.getByRole("spinbutton").fill("82");
	await page.getByRole("button", { name: /Adicionar Nota/ }).click();
	await expect(page.getByRole("row", { name: /Lanna Correia/ })).toContainText(
		"82.0",
	);

	await page.getByRole("textbox", { name: "Buscar por nome" }).fill("lanna");
	await expect(page.getByRole("row", { name: /Lanna Correia/ })).toBeVisible();
	await expect(page.getByRole("row", { name: /Ana Clara Souza/ })).toHaveCount(
		0,
	);
});

test("selects and updates a student", async ({ page }) => {
	await page.getByRole("row", { name: /Carlos Eduardo Lima/ }).click();
	await page.getByPlaceholder("Digite o nome completo").fill("Carlos Lima");
	await page.getByRole("spinbutton").fill("64");
	await page.getByRole("button", { name: /Atualizar/ }).click();
	await expect(page.getByRole("row", { name: /Carlos Lima/ })).toContainText(
		"64.0",
	);
});

test("replaces a grade of a selected student", async ({ page }) => {
	await page.getByRole("row", { name: /Ana Clara Souza/ }).click();
	await page.getByRole("spinbutton").fill("65");
	await page.getByRole("button", { name: /Substituir/ }).click();
	await expect(
		page.getByRole("row", { name: /Ana Clara Souza/ }),
	).toContainText("65.0");
});

test("deletes a student", async ({ page }) => {
	page.once("dialog", (dialog) => dialog.accept());
	await page.getByRole("row", { name: /Juliana Mendes/ }).click();
	await page
		.getByRole("row", { name: /Juliana Mendes/ })
		.getByRole("button", { name: "Excluir Juliana Mendes" })
		.click();
	await expect(page.getByRole("row", { name: /Juliana Mendes/ })).toHaveCount(
		0,
	);
});
