# FactsCLI

A modern Python CLI application that stores and retrieves categorized facts with both command-line and text-based user interfaces. Built with security-first architecture featuring encrypted credential storage, Argon2 password hashing, and persistent authentication.

## Features

- **Dual Interface**: Choose between a simple CLI (Typer) or an interactive TUI (Textual)
- **Categorized Facts**: Organize facts into happy, sad, and fun categories
- **User Authentication**: Secure signup/login with Argon2 password hashing
- **Persistent Sessions**: Encrypted session storage using keyring
- **Database Flexibility**: SQLite for development, PostgreSQL for production
- **LLM Integration**: AI-powered fact generation and management using LangChain and LangGraph
- **Database Migrations**: Alembic-powered schema versioning

## Screenshots

### CLI Interface

![CLI Interface](screenshots/cli.png)

### TUI Interface

![TUI Interface](screenshots/tui.png)

## Tools & Technologies

### Core Framework
- **Python 3.13+**: Modern Python with latest language features
- **Typer**: CLI framework with automatic help generation and type hints
- **Textual**: Modern TUI framework for building terminal applications
- **Rich**: Beautiful terminal formatting and output

### Database & ORM
- **SQLAlchemy 2.0**: Modern Python ORM with full typing support
- **Alembic**: Database migration management
- **PostgreSQL**: Production database (via psycopg2-binary)
- **SQLite**: Development database (built-in)

### Security
- **Passlib**: Password hashing library with Argon2 support
- **Keyring**: Encrypted credential storage
- **CryptFile**: File-based encrypted keyring backend
- **Argon2**: Memory-hard password hashing algorithm

### AI/LLM
- **LangChain**: LLM application framework
- **LangGraph**: State machine for AI workflows
- **OpenAI Integration**: LLM-powered features

### Development Tools
- **UV**: Fast Python package installer and resolver
- **Pydantic**: Data validation using Python type hints
- **python-dotenv**: Environment variable management

## Project Setup

### Prerequisites

- Python 3.13 or higher
- UV package manager (recommended) or pip
- PostgreSQL (optional, for production use)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Facts
   ```

2. **Install UV (if not already installed)**
   ```bash
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and set your values
   # Required:
   # - KEYRING_PASSWORD: Master password for encrypted credential storage
   # - LLM: LLM name
   # - LLM_API_KEY: API key for your LLM provider
   # Optional:
   # - FACTCLI_DATABASE_URL: Database connection string (defaults to SQLite)
   # - LLM_BASE_URL: Custom base URL for LLM API (if using local/custom endpoint)
   ```

5. **Initialize the database**
   ```bash
   # Run migrations (creates tables)
   alembic upgrade head

   # Or simply run the app (auto-creates tables)
   uv run python main.py
   ```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Required: Master password for encrypted keyring storage
KEYRING_PASSWORD=your-secure-password-here

# Required: LLM configuration
LLM=llama3.2:latest
LLM_API_KEY=your-llm-api-key-here

# Optional: Database connection string
# Defaults to SQLite at ./database.sqlite3
FACTCLI_DATABASE_URL=sqlite:///database.sqlite3
# For PostgreSQL:
# FACTCLI_DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/facts

# Optional: Custom LLM endpoint (for local models or custom deployments)
LLM_BASE_URL=http://localhost:11434  # Example for Ollama
```

## Usage

### CLI Commands

```bash
# Show help and available commands
uv run python main.py --help

# Get a random fact by category
uv run python main.py happy    # Get a happy fact
uv run python main.py sad      # Get a sad fact
uv run python main.py fun      # Get a fun fact

# Add a new fact
uv run python main.py add happy "Your fact text here"
uv run python main.py add sad "Another fact"
uv run python main.py add fun "Fun fact!"

# User management
uv run python main.py whoami   # Show logged-in user
uv run python main.py signout  # Sign out current user

# Launch the TUI
uv run python main.py ui
```

### TUI (Text User Interface)

Launch the interactive terminal UI:

```bash
uv run python main.py ui
```

**Navigation:**
- Login or signup when first launched
- Use Tab/Shift+Tab to navigate between fields
- Press Enter to submit forms
- Navigate through menu options using arrow keys or buttons
- Press Ctrl+C or use quit button to exit

## Architecture

### Project Structure

```
Facts/
├── app/                    # Core application logic
│   ├── agent.py           # LLM agent integration
│   ├── auth.py            # Authentication and password hashing
│   ├── cli.py             # CLI command handlers
│   ├── fact_handler.py    # Fact management logic
│   ├── facts.py           # Core facts business logic
│   ├── schema.py          # Pydantic schemas
│   └── session_store.py   # Session restoration
├── conf/                   # Configuration modules
│   ├── database.py        # Database setup and connection
│   └── env.py             # Environment variable handling
├── models/                 # SQLAlchemy data models
│   ├── fact.py            # Fact model
│   ├── session_token.py   # SessionToken model
│   ├── user.py            # User model
│   └── user_fact.py       # UserFact relationship model
├── screens/                # Textual TUI screens
│   ├── add_fact.py        # Add fact screen
│   ├── login.py           # Login screen
│   ├── menu.py            # Main menu screen
│   ├── show_fact.py       # Display fact screen
│   └── signup.py          # User registration screen
├── styles/                 # TUI styling
│   └── app.tcss           # Textual CSS
├── migrations/             # Alembic database migrations
├── main.py                 # Application entry point
├── tui.py                  # TUI application setup
└── .env                    # Environment configuration (not in git)
```

### Data Models

- **User**: Stores username and Argon2-hashed password
- **Fact**: Stores category (happy/sad/fun) and fact text
- **UserFact**: Many-to-many relationship between users and facts
- **SessionToken**: UUID-based session tokens for persistent authentication

### Security Features

**Password Security:**
- Argon2 hashing with memory-hard parameters (100MB memory cost)
- Time cost: 2, Parallelism: 8
- Passwords never stored in plain text

**Session Management:**
- UUID-based session tokens stored in database
- Local tokens encrypted using CryptFile keyring
- Keyring protected by `KEYRING_PASSWORD` environment variable
- Automatic session restoration on app launch

## Database Management

### Running Migrations

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current
```

### Database Configuration

The app supports both SQLite (default) and PostgreSQL:

**SQLite (Development):**
```bash
FACTCLI_DATABASE_URL=sqlite:///database.sqlite3
```

**PostgreSQL (Production):**
```bash
FACTCLI_DATABASE_URL=postgresql://username:password@localhost:5432/factcli
```

## Development

### Running in Development Mode

```bash
# Run with auto-reload (if configured)
uv run python main.py ui

# Run CLI commands directly
uv run python main.py <command>
```

### Adding New Features

1. **Models**: Add new SQLAlchemy models in [models/](models/)
2. **Migrations**: Generate migration with `alembic revision --autogenerate`
3. **Business Logic**: Add logic to [app/](app/) modules
4. **CLI Commands**: Add commands in [app/cli.py](app/cli.py)
5. **TUI Screens**: Create new screens in [screens/](screens/)
6. **Styling**: Update [styles/app.tcss](styles/app.tcss)
