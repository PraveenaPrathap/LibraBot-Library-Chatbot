# Lumina Library Chatbot

A Streamlit library assistant with book search, category recommendations,
borrowing status queries, user registration and login, saved chat history,
and a question-and-answer knowledge base. It uses SQLite for local storage
and NLTK with scikit-learn for text matching.

## Setup and run

Install Python and run these commands from the project folder:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start the application:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Internet access is needed for
dependency installation and the first download of NLTK resources (`punkt`,
`punkt_tab`, and `wordnet`).

The application automatically creates `lumina_library.db` and its tables.
If `library_data.csv` is present in the project folder, it imports that data
during application initialization. Without the CSV, the database starts empty.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface and application flow |
| `database_manager.py` | SQLite tables, data import, and queries |
| `nlp_engine.py` | Query intent detection and text matching |
| `requirements.txt` | Python dependencies |
| `library_data.csv` | Initial library and borrowing data |
| `.gitignore` | Excludes generated files, local databases, and secrets |
| `README.md` | Project overview and setup instructions |

## Uploading to GitHub

Upload the three Python files, `requirements.txt`, `.gitignore`, and this
`README.md`. Include `library_data.csv` only if it contains sample data or
data you are authorized to publish. It includes user IDs and borrowing
details; anonymize real user records before publishing. The existing CSV
has not been verified as synthetic data.

Do not upload `lumina_library.db`, `__pycache__/`, virtual environments,
`.env` files, `.streamlit/secrets.toml`, or `temp_library_data.csv`.
These are covered by `.gitignore` when using Git. When uploading through
the GitHub website, select files manually according to this list.

## Current limitation

The current login implementation stores passwords as plain text in the
local database. Use demo credentials only; password hashing and a security
review are needed before using this application with real accounts.
