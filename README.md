# C216-L
Repository for all projects and general codes developed for distributed systems laboratory class.

## Branches:

### Aulas

Codes for classes contents.

### Projeto final - Books Rater

### O projeto

## Tema

O projeto apresenta uma plataforma de anotação sobre livros já lidos, permitindo que o usuário insira o título, autor, avaliação e nota para um determinado livro de sua escolha.

## Objetivo

O projeto tem por objetivo exercitar e fixar os aprendizados adquiridos em aula sobre arquiteturas e estruturação de um trabalho full-stack.

## Tecnologias utilizadas

Este projeto utiliza as tecnologias: 

Backend: Python, FastAPI, SQLAlchemy, Alembic, Poetry e Ruff;
Frontend: Typescript, React, Vite;
Teste: Pytest, Vitest, Playwright, Jsdom, Testing Library;
Banco de dados: PostgreSQL(Docker);
Infraestrutura e CI: GitHub Actions, Docker e Make.

## Funcionalidades

- Login de um usuário único, com credenciais configuradas por variável de ambiente;
- Sessão que expira a cada 10 minutos de usuário logado;
- Cadastro de livros com avaliação, título, autor, nota e anotações;
- Atualização de um livro já cadastrado pelo envio do mesmo título;
- Exclusão de um livro por título;
- Listas de notas e avaliações atualizadas a partir do banco, garantindo persistência;
- O banco de dados rejeita livros de mesmo título, fazendo a atualização dos dados do mesmo ao invés de gerar um novo.

## Estrutura

- Geral

O projeto é organizado em um repositório único com arquitetura em camada com duas aplicações independentes, o backend e o frontend, mais os arquivos de infraestrutura na raiz. O backend, escrito em Python com FastAPI, concentra a API: as rotas de livros e de login ficam em app/api/routes, os modelos do SQLAlchemy em app/models, os schemas de validação do Pydantic em app/schemas e a configuração da conexão com o PostgreSQL em app/database, enquanto o main.py reúne tudo. O frontend, escrito em TypeScript com React e Vite, tem o App.tsx como controlador que alterna entre as páginas de Login e Home, localizadas em src/pages, e que consomem a API por meio de requisições. O banco de dados PostgreSQL roda em um container Docker, e as mudanças em sua estrutura são versionadas com migrações do Alembic. Os testes acompanham cada lado: no backend, o Pytest cobre testes unitários e de integração; no frontend, o Vitest com Testing Library valida os componentes, e o Playwright, em uma pasta e2e, testa o fluxo completo no navegador com os dois servidores no ar. Por fim, o Makefile reúne atalhos para lint, testes e execuções, e os workflows do GitHub Actions, em .github/workflows, executam automaticamente a verificação de código e os testes do backend e do frontend a cada push e pull request.

- API
 
| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/auth/login` | Autentica com e-mail e senha |
| `GET` | `/books/` | Lista os livros |
| `GET` | `/books/{id}` | Busca um livro pelo id |
| `POST` | `/books/` | Cria um livro |
| `PATCH` | `/books/{id}` | Atualiza campos de um livro |
| `PUT` | `/books/{id}` | Substitui um livro |
| `DELETE` | `/books/{id}` | Exclui um livro |
| `GET` | `/health` | Verificação de saúde |
 
A documentação interativa fica em `http://localhost:8000/docs` com o backend no ar.

## Pré-requisitos

- Python 3.12 ou superior;
- Poetry;
- Node.js 22 ou superior;
- npm;
- Docker;
- Make.

## Como executar
 
### Via Docker
 
```bash
make up-build 
```

E abrir `http://localhost:8000/healthy` para verificar a saúde do backend e `http://localhost:5173/` para ter acesso ao frontend.
 
## Migrações
 
As migrações são feitas com Alembic, a partir da pasta `backend/`:
 
```bash
# aplicar todas as migrações
poetry run alembic upgrade head
 
# criar uma nova migração a partir das mudanças nos modelos
poetry run alembic revision --autogenerate -m "descrição da mudança"
 
# desfazer a última migração
poetry run alembic downgrade -1
```

## Testes
 
O projeto tem testes unitários, de integração e end-to-end.
 
| Camada | Backend | Frontend |
|---|---|---|
| Unitários | `pytest tests/unit`: schemas e modelo | Vitest: lógica de sessão no App |
| Integração | `pytest tests/integration`: rotas com PostgreSQL | Vitest: Home, Login e App com fetch simulado |
| End-to-end | | Playwright: login, criar, atualizar e excluir livros |
 
### Banco de teste
 
Os testes de integração usam um banco separado, para nunca alterar os dados de desenvolvimento. Crie-o uma vez, ajustando o nome do container e do usuário:
 
```bash
docker exec -it NOME_DO_CONTAINER createdb -U USUARIO books_test
```
 
Defina a URL de teste ao rodar:
 
```bash
export TEST_DATABASE_URL='postgresql+psycopg://USUARIO:SENHA@localhost:5432/books_test'
```
 
O nome do banco precisa terminar em `_test`: o `conftest.py` recusa qualquer outro, porque cada teste cria e apaga toda a tabela.


## Vídeo de execução

Abaixo está o link do vídeo explicativo do projeto:

https://youtu.be/PzlrZ8vrj-g