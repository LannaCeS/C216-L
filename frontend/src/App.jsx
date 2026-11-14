import { useEffect, useMemo, useState } from "react";
import {
	createGrade,
	deleteAllGrades,
	listGrades,
	replaceGrade,
	updateGrade,
} from "./services/grades";

function App() {
	const [students, setStudents] = useState([]);
	const [_loadError, setLoadError] = useState("");
	useEffect(() => {
		listGrades()
			.then((grades) => {
				setStudents(
					grades.map((item) => ({
						...item,
						id: item.name,
					})),
				);
			})
			.catch((error) => setLoadError(error.message));
	}, []);
	const [selectedId, setSelectedId] = useState(null);
	const [name, setName] = useState("");
	const [grade, setGrade] = useState("");
	const [search, setSearch] = useState("");
	const selected = students.find((student) => student.id === selectedId);
	const visibleStudents = useMemo(
		() =>
			students.filter((student) =>
				student.name.toLowerCase().includes(search.toLowerCase()),
			),
		[students, search],
	);

	function clearSelection() {
		setSelectedId(null);
		setName("");
		setGrade("");
	}

	function selectStudent(student) {
		setSelectedId(student.id);
		setName(student.name);
		setGrade(String(student.grade));
	}

	function validForm() {
		const numericGrade = Number(grade);
		if (!name.trim()) {
			window.alert("Por favor, informe o nome do aluno.");
			return false;
		}
		if (
			grade === "" ||
			!Number.isFinite(numericGrade) ||
			numericGrade < 0 ||
			numericGrade > 100
		) {
			window.alert("Por favor, informe uma nota válida entre 0.0 e 100.0.");
			return false;
		}
		return true;
	}

	async function addStudent() {
		if (!validForm()) return;
		try {
			const result = await createGrade(name.trim(), Number(grade));

			setStudents(
				result.map((item) => ({
					...item,
					id: item.name,
				})),
			);
			clearSelection();
		} catch (error) {
			window.alert(error.message);
		}
	}

	async function updateStudent() {
		if (!selected)
			return window.alert("Selecione um aluno da tabela para atualizar.");
		if (!validForm()) return;
		try {
			await replaceGrade(name.trim(), Number(grade));
			setStudents((current) =>
				current.map((student) =>
					student.id === selected.id
						? { ...student, name: name.trim(), grade: Number(grade) }
						: student,
				),
			);
		} catch (error) {
			window.alert(error.message);
		}
	}

	async function replaceaGrade() {
		if (!selected)
			return window.alert(
				"Selecione uma linha para efetuar a substituição completa.",
			);
		const result = await updateGrade(name.trim(), Number(grade));
		if (
			grade === "" ||
			!Number.isFinite(Number(grade)) ||
			Number(grade) < 0 ||
			Number(grade) > 100
		) {
			return window.alert("Informe a nova nota que substituirá a atual.");
		}
		setStudents(result.map((item) => ({ ...item, id: item.name })));
	}

	async function deleteAll() {
		if (!window.confirm("Tem certeza que deseja excluir TODAS as notas?"))
			return;
		try {
			await deleteAllGrades();
			setStudents([]);
			clearSelection();
		} catch (error) {
			window.alert(error.message);
		}
	}

	return (
		<>
			<header className="topbar">
				<div className="topbar-inner">
					<div className="brand">
						<div className="brand-icon">
							<span className="material-symbols-outlined">school</span>
						</div>
						<div>
							<strong>Portal do Professor</strong>
							<small>Gestão de Notas</small>
						</div>
					</div>
					<div className="profile">
						<div>
							<strong>Prof. Carlos Eduardo</strong>
							<small>Departamento Acadêmico</small>
						</div>
						<span className="avatar material-symbols-outlined">person</span>
					</div>
				</div>
			</header>

			<main className="page">
				<h1>Lançamento e Controle de Notas</h1>
				<section className="form-card">
					<div className="section-title">
						<span className="title-icon material-symbols-outlined">
							edit_note
						</span>
						<h2>Formulário de Aluno</h2>
					</div>
					<div className="fields">
						<label className="field name-field">
							Nome do Aluno
							<span className="input-wrap">
								<span className="material-symbols-outlined">person</span>
								<input
									value={name}
									onChange={(event) => setName(event.target.value)}
									placeholder="Digite o nome completo"
								/>
							</span>
						</label>
						<label className="field">
							Nota (0.0 a 100.0)
							<span className="input-wrap">
								<span className="material-symbols-outlined">score</span>
								<input
									type="number"
									min="0"
									max="100"
									step="0.1"
									value={grade}
									onChange={(event) => setGrade(event.target.value)}
									placeholder="0"
								/>
							</span>
						</label>
					</div>
					<div className="actions">
						<button
							type="button"
							className="button primary"
							onClick={addStudent}
						>
							<span className="material-symbols-outlined">add_circle</span>
							Adicionar Nota
						</button>
						<button
							type="button"
							className="button secondary"
							onClick={updateStudent}
						>
							<span className="material-symbols-outlined">
								published_with_changes
							</span>
							Atualizar
						</button>
						<button
							type="button"
							className="button neutral"
							onClick={replaceaGrade}
						>
							<span className="material-symbols-outlined">swap_horiz</span>
							Substituir
						</button>
						<button type="button" className="button danger" onClick={deleteAll}>
							<span className="material-symbols-outlined">delete_sweep</span>
							Deletar todas
						</button>
						{selected && (
							<button
								type="button"
								className="text-button"
								onClick={clearSelection}
							>
								Limpar seleção
							</button>
						)}
					</div>
				</section>

				<section className="table-card">
					<div className="table-heading">
						<div>
							<h2>Tabela de Notas</h2>
							<p>Registros de alunos cadastrados</p>
						</div>
						<form
							className="search"
							onSubmit={(event) => event.preventDefault()}
						>
							<label className="search-input">
								<span className="material-symbols-outlined">search</span>
								<input
									aria-label="Buscar por nome"
									value={search}
									onChange={(event) => setSearch(event.target.value)}
									placeholder="Buscar por nome..."
								/>
							</label>
							<button type="submit" className="button primary search-button">
								<span className="material-symbols-outlined">search</span>Buscar
							</button>
						</form>
					</div>
					<div className="table-scroll">
						<table>
							<thead>
								<tr>
									<th>Aluno</th>
									<th className="grade-column">Nota Final</th>
								</tr>
							</thead>
							<tbody>
								{visibleStudents.map((student) => {
									return (
										<tr
											key={student.id}
											className={selectedId === student.id ? "selected" : ""}
											onClick={() => selectStudent(student)}
										>
											<td>
												<span className="student-name">{student.name}</span>
											</td>
											<td className="grade-column">
												<span className="grade">
													{student.grade.toFixed(1)}
												</span>
											</td>
										</tr>
									);
								})}
							</tbody>
						</table>
						{visibleStudents.length === 0 && (
							<p className="empty-state">Nenhum aluno encontrado.</p>
						)}
					</div>
					<div className="pagination">
						<button type="button" aria-label="Página anterior" disabled>
							<span className="material-symbols-outlined">chevron_left</span>
						</button>
						<span className="current-page">1</span>
						<button type="button" aria-label="Próxima página" disabled>
							<span className="material-symbols-outlined">chevron_right</span>
						</button>
					</div>
				</section>
			</main>
			<footer className="footer">
				Portal do Professor <span>•</span> Gestão de Notas
			</footer>
		</>
	);
}

export default App;
