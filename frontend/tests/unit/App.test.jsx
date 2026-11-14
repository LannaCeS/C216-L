import {
	cleanup,
	fireEvent,
	render,
	screen,
	waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App.jsx";

const api = vi.hoisted(() => ({
	listGrades: vi.fn(),
	createGrade: vi.fn(),
	updateGrade: vi.fn(),
	deleteAllGrades: vi.fn(),
	replaceGrade: vi.fn(),
}));

vi.mock("../../src/services/grades", () => api);

const initialStudents = [
	{ name: "Ana Clara Souza", grade: 95 },
	{ name: "Bruno Henrique Costa", grade: 44.2 },
	{ name: "Carlos Eduardo Lima", grade: 70 },
	{ name: "Daniela Ferreira", grade: 65.5 },
	{ name: "Gabriel Martins", grade: 88.3 },
	{ name: "Juliana Mendes", grade: 58 },
];

afterEach(() => {
	cleanup();
	vi.restoreAllMocks();
});

beforeEach(() => {
	api.listGrades.mockResolvedValue(initialStudents);
	api.createGrade.mockResolvedValue([
		{ name: "Marina Alves", grade: 82 },
		...initialStudents,
	]);
	api.updateGrade.mockResolvedValue(
		initialStudents.map((student) =>
			student.name === "Ana Clara Souza" ? { ...student, grade: 65 } : student,
		),
	);
	api.replaceGrade.mockResolvedValue(initialStudents);
	api.deleteAllGrades.mockResolvedValue({ message: "All grades deleted." });
});

function rowFor(name) {
	return screen.getByRole("row", { name: new RegExp(name) });
}

describe("grade management", () => {
	it("loads the students from the mocked API", async () => {
		render(<App />);

		expect(
			await screen.findByRole("row", { name: /Ana Clara Souza/ }),
		).toHaveTextContent("95.0");
		expect(rowFor("Bruno Henrique Costa")).toHaveTextContent("44.2");
		expect(api.listGrades).toHaveBeenCalledOnce();
	});

	it("adds a student and rejects a grade outside the allowed range", async () => {
		render(<App />);
		await screen.findByRole("row", { name: /Ana Clara Souza/ });
		fireEvent.change(screen.getByPlaceholderText("Digite o nome completo"), {
			target: { value: "Marina Alves" },
		});
		fireEvent.change(screen.getByRole("spinbutton"), {
			target: { value: "82" },
		});
		fireEvent.click(screen.getByRole("button", { name: /Adicionar Nota/ }));
		expect(
			await screen.findByRole("row", { name: /Marina Alves/ }),
		).toHaveTextContent("82.0");
		expect(api.createGrade).toHaveBeenCalledWith("Marina Alves", 82);

		const alert = vi.spyOn(window, "alert").mockImplementation(() => {});
		fireEvent.change(screen.getByPlaceholderText("Digite o nome completo"), {
			target: { value: "Invalid Grade" },
		});
		fireEvent.change(screen.getByRole("spinbutton"), {
			target: { value: "101" },
		});
		fireEvent.click(screen.getByRole("button", { name: /Adicionar Nota/ }));
		expect(alert).toHaveBeenCalledWith(
			"Por favor, informe uma nota válida entre 0.0 e 100.0.",
		);
		expect(
			screen.queryByRole("row", { name: /Invalid Grade/ }),
		).not.toBeInTheDocument();
	});

	it("updates the selected student's name and grade", async () => {
		render(<App />);
		fireEvent.click(
			await screen.findByRole("row", { name: /Carlos Eduardo Lima/ }),
		);
		fireEvent.change(screen.getByPlaceholderText("Digite o nome completo"), {
			target: { value: "Carlos Lima" },
		});
		fireEvent.change(screen.getByRole("spinbutton"), {
			target: { value: "64" },
		});
		fireEvent.click(screen.getByRole("button", { name: /Atualizar/ }));
		expect(
			await screen.findByRole("row", { name: /Carlos Lima/ }),
		).toHaveTextContent("64.0");
		expect(
			screen.queryByRole("row", { name: /Carlos Eduardo Lima/ }),
		).not.toBeInTheDocument();
	});

	it("replaces the selected grade and filters by student name", async () => {
		render(<App />);
		fireEvent.click(
			await screen.findByRole("row", { name: /Ana Clara Souza/ }),
		);
		fireEvent.change(screen.getByRole("spinbutton"), {
			target: { value: "65" },
		});
		fireEvent.click(screen.getByRole("button", { name: /Substituir/ }));
		expect(
			await screen.findByRole("row", { name: /Ana Clara Souza/ }),
		).toHaveTextContent("65.0");

		fireEvent.change(screen.getByRole("textbox", { name: "Buscar por nome" }), {
			target: { value: "ana" },
		});
		expect(rowFor("Ana Clara Souza")).toBeInTheDocument();
		expect(
			screen.queryByRole("row", { name: /Bruno Henrique Costa/ }),
		).not.toBeInTheDocument();
	});

	it("deletes all grades after confirmation", async () => {
		vi.spyOn(window, "confirm").mockReturnValue(true);
		render(<App />);
		await screen.findByRole("row", { name: /Juliana Mendes/ });
		fireEvent.click(screen.getByRole("button", { name: /Deletar todas/ }));
		await waitFor(() => expect(api.deleteAllGrades).toHaveBeenCalledOnce());
		expect(
			screen.queryByRole("row", { name: /Juliana Mendes/ }),
		).not.toBeInTheDocument();
	});
});
