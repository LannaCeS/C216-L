import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App.jsx";

afterEach(() => {
	cleanup();
	vi.restoreAllMocks();
});

function rowFor(name) {
	return screen.getByRole("row", { name: new RegExp(name) });
}

describe("grade management", () => {
	it("shows the initial students and their result statuses", () => {
		render(<App />);

		expect(rowFor("Ana Clara Souza")).toHaveTextContent("95.0");
		expect(rowFor("Bruno Henrique Costa")).toHaveTextContent("44.2");
	});

	it("adds a student and rejects a grade outside the allowed range", () => {
		render(<App />);
		fireEvent.change(screen.getByPlaceholderText("Digite o nome completo"), {
			target: { value: "Marina Alves" },
		});
		fireEvent.change(screen.getByRole("spinbutton"), {
			target: { value: "82" },
		});
		fireEvent.click(screen.getByRole("button", { name: /Adicionar Nota/ }));
		expect(rowFor("Marina Alves")).toHaveTextContent("82.0");

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

	it("selects a row and updates its name and grade", () => {
		render(<App />);
		fireEvent.click(rowFor("Carlos Eduardo Lima"));
		expect(screen.getByPlaceholderText("Digite o nome completo")).toHaveValue(
			"Carlos Eduardo Lima",
		);
		expect(screen.getByRole("spinbutton")).toHaveValue(70);

		fireEvent.change(screen.getByPlaceholderText("Digite o nome completo"), {
			target: { value: "Carlos Lima" },
		});
		fireEvent.change(screen.getByRole("spinbutton"), {
			target: { value: "64" },
		});
		fireEvent.click(screen.getByRole("button", { name: /Atualizar/ }));
		expect(rowFor("Carlos Lima")).toHaveTextContent("64.0");
		expect(
			screen.queryByRole("row", { name: /Carlos Eduardo Lima/ }),
		).not.toBeInTheDocument();
	});

	it("replaces the selected grade and filters by student name", () => {
		render(<App />);
		fireEvent.click(rowFor("Ana Clara Souza"));
		fireEvent.change(screen.getByRole("spinbutton"), {
			target: { value: "65" },
		});
		fireEvent.click(screen.getByRole("button", { name: /Substituir/ }));
		expect(rowFor("Ana Clara Souza")).toHaveTextContent("65.0");

		fireEvent.change(screen.getByRole("textbox", { name: "Buscar por nome" }), {
			target: { value: "ana" },
		});
		expect(
			screen.getByRole("row", { name: /Ana Clara Souza/ }),
		).toBeInTheDocument();
		expect(
			screen.queryByRole("row", { name: /Bruno Henrique Costa/ }),
		).not.toBeInTheDocument();
	});

	it("deletes a selected student after confirmation", () => {
		vi.spyOn(window, "confirm").mockReturnValue(true);
		render(<App />);
		fireEvent.click(rowFor("Juliana Mendes"));
		fireEvent.click(
			screen.getByRole("button", { name: "Excluir Juliana Mendes" }),
		);
		expect(
			screen.queryByRole("row", { name: /Juliana Mendes/ }),
		).not.toBeInTheDocument();
	});
});
