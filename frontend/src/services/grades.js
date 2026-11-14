export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8888";
const GRADES_URL = `${API_URL}/settings/grade`;

async function request(url, options, errorMessage) {
	const response = await fetch(url, options);
	if (!response.ok) {
		const body = await response.json().catch(() => null);
		const detail = Array.isArray(body?.detail)
			? body.detail.map((item) => item.msg ?? JSON.stringify(item)).join("; ")
			: (body?.detail ?? body?.message);
		throw new Error(
			detail
				? `${errorMessage} (${response.status}): ${detail}`
				: `${errorMessage} (HTTP ${response.status})`,
		);
	}
	return response.json();
}

export function listGrades() {
	return request(GRADES_URL, undefined, "Erro ao carregar as notas.");
}

export function createGrade(name, grade) {
	return request(
		GRADES_URL,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ name, grade: grade }),
		},
		"Erro ao cadastrar a nota.",
	);
}

export function updateGrade(name, grade) {
	return request(
		GRADES_URL,
		{
			method: "PUT",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ name, grade: grade }),
		},
		"Erro ao atualizar a nota.",
	);
}

export function deleteAllGrades() {
	return request(
		GRADES_URL,
		{
			method: "DELETE",
		},
		"Erro ao deletar as notas.",
	);
}

export function replaceGrade(name, grade) {
	return request(
		GRADES_URL,
		{
			method: "PATCH",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ name, grade: grade }),
		},
		"Erro ao substituir a nota.",
	);
}
