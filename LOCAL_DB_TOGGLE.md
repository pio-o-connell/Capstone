Local DB Toggle
=================

Purpose
-------
Short instructions to switch between SQLite (local default) and Postgres for local development.

How it works in this project
---------------------------
- By default the project uses SQLite (file `db.sqlite3`).
- If either `USE_POSTGRES` is set to a truthy value (e.g. `1`) or `DATABASE_URL` is present in the environment, `config/settings.py` will switch the `DATABASES` setting to Postgres.
- The repository includes an `env.py` (local-only convenience) that calls `os.environ.setdefault('USE_POSTGRES','1')` and provides a `DATABASE_URL` for local testing. `config/settings.py` imports `env.py` if that file exists.

Quick commands
--------------
PowerShell (current session only):

```
$env:USE_POSTGRES = '1'
# or set DATABASE_URL directly
$env:DATABASE_URL = 'postgresql://user:pass@host:port/dbname'
```

Bash (current session only):

```
export USE_POSTGRES=1
# or
export DATABASE_URL='postgresql://user:pass@host:port/dbname'
```

Make it persistent on Windows (new shells):

```
setx USE_POSTGRES "1"
```

Undo (return to SQLite)
-----------------------
PowerShell:
```
Remove-Item Env:\USE_POSTGRES
# or
Remove-Item Env:\DATABASE_URL
```

Bash:
```
unset USE_POSTGRES
# or
unset DATABASE_URL
```

If `env.py` exists in the project root it will set defaults when `config/settings.py` imports it — remove or edit `env.py` to stop the default local Postgres behavior.

Script files
------------
I also added ready-to-run script files under `scripts/` so you can run the toggles directly:

- PowerShell script: `scripts/toggle_db.ps1`
- Bash script: `scripts/toggle_db.sh`

How to run
----------
PowerShell (run in project root):

```powershell
# Run the PS script (may require execution policy or dot-sourcing in some environments):
.\scripts\toggle_db.ps1 postgres
.\scripts\toggle_db.ps1 sqlite
.\scripts\toggle_db.ps1 status
```

Bash (make executable first on Windows WSL / Linux / macOS):

```bash
chmod +x ./scripts/toggle_db.sh
./scripts/toggle_db.sh postgres
./scripts/toggle_db.sh sqlite
./scripts/toggle_db.sh status
```

These scripts modify only the current shell environment. To make persistent systemwide changes, set the environment variables in your OS or edit/remove `env.py` in the project root.

Apply migrations after switching
-------------------------------
Whenever you switch the active database you should run migrations to ensure the schema is present on the target DB:

```
.venv\Scripts\python.exe manage.py migrate
```

Verify which DB Django is using (quick check)
-------------------------------------------
Run this Python snippet (PowerShell or bash):

```
.venv\Scripts\python.exe -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); import django; django.setup(); from django.db import connections; print(connections['default'].settings_dict)"
```

Notes
-----
- On production platforms (Heroku, Neon, etc.) prefer setting `DATABASE_URL` in the environment rather than using `env.py`.
- `dj-database-url` and `psycopg2-binary` are used to parse `DATABASE_URL` and connect to Postgres — ensure they are in `requirements.txt` (they are included in this repo).
- Do not commit real credentials to version control. Keep `env.py` local-only and add it to `.gitignore` if you haven't already.

Questions?
----------
If you want I can add this short note to another filename or include it in the README instead. I can also add a small script to toggle env vars for you.
