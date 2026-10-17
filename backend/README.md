# Backend

## Run PostgreSQL local

1. Copy `.env.example` to `.env` at the repository root and change the password.
2. Start the database and API with `make up-and-build`.
3. Apply schema migrations with `make db-upgrade`.
4. Import existing JSON grades with `make db-import-grades`.

When running the API directly on your machine (`make run-backend`), the default connection uses `localhost:5433`. The host port can be changed with `POSTGRES_PORT` in `.env`;

Database credentials in `.env` are for local development only. The PostgreSQL
data is persisted in the `postgres_data` Docker volume.
The JSON file remains as a backup; the API reads and writes grades in
PostgreSQL after the migration. The import command skips names already present
in the database, so it can be rerun safely.

To create a migration after changing SQLAlchemy models, run:

```sh
make db-migration msg="describe the schema change"
make db-upgrade
```

## PostgreSQL integration test

The API integration test uses a separate, disposable PostgreSQL database. Set
`TEST_DATABASE_URL` to that database, apply migrations to it, then run the
integration target. With Compose running, create a dedicated test database:

```sh
docker-compose exec -T db sh -c 'createdb -U "$POSTGRES_USER" app_test'
export TEST_DATABASE_URL="postgresql+psycopg://postgres:<URL_ENCODED_PASSWORD>@localhost:5433/app_test"
cd backend
DATABASE_URL="$TEST_DATABASE_URL" poetry run alembic upgrade head
cd ..
make test-integration
```

Replace `<URL_ENCODED_PASSWORD>` with the actual `POSTGRES_PASSWORD` from the
root `.env` file. If that password contains URL-reserved characters, percent
encode them. The password must also match the role password already stored in
the PostgreSQL volume; changing `.env` alone does not change an initialized
database user's password.

The test creates a uniquely named record and removes it afterward. It does not
reset or truncate the database.
