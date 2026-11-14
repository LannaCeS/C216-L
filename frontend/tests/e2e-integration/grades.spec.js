import { expect, test } from "@playwright/test";

const initialStudents = [
	{ name: "Ana Clara Souza", grade: 95 },
	{ name: "Bruno Henrique Costa", grade: 44.2 },
	{ name: "Carlos Eduardo Lima", grade: 70 },
	{ name: "Daniela Ferreira", grade: 65.5 },
	{ name: "Gabriel Martins", grade: 88.3 },
	{ name: "Juliana Mendes", grade: 58 },
];

test.beforeEach(async ({ page }) => {
	let students = initialStudents.map((student) => ({ ...student }));
	await page.route("**/settings/grade", async (route) => {
		const method = route.request().method();
		if (method === "GET") {
			return route.fulfill({ json: students });
		}
		if (method === "POST") {
			students = [{ ...route.request().postDataJSON() }, ...students];
			return route.fulfill({ json: students });
		}
		if (method === "PATCH" || method === "PUT") {
			const body = route.request().postDataJSON();
			students = students.map((student) =>
				student.name.toLowerCase() === body.name.toLowerCase()
					? { ...student, grade: body.grade }
					: student,
			);
			return route.fulfill({ json: students });
		}
		if (method === "DELETE") {
			students = [];
			return route.fulfill({ json: { message: "All grades deleted." } });
		}
		return route.continue();
	});
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
	await page.getByRole("spinbutton").fill("64");
	await page.getByRole("button", { name: /Atualizar/ }).click();
	await expect(
		page.getByRole("row", { name: /Carlos Eduardo Lima/ }),
	).toContainText("64.0");
});

test("replaces a grade of a selected student", async ({ page }) => {
	await page.getByRole("row", { name: /Ana Clara Souza/ }).click();
	await page.getByRole("spinbutton").fill("65");
	await page.getByRole("button", { name: /Substituir/ }).click();
	await expect(
		page.getByRole("row", { name: /Ana Clara Souza/ }),
	).toContainText("65.0");
});

test("deletes all students after confirmation", async ({ page }) => {
	page.once("dialog", (dialog) => dialog.accept());
	await page.getByRole("button", { name: /Deletar todas/ }).click();
	await expect(page.getByRole("row", { name: /Ana Clara Souza/ })).toHaveCount(
		0,
	);
	await expect(page.getByText("Nenhum aluno encontrado.")).toBeVisible();
});
