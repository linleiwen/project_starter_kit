# [Project Name] - Python Project Template

[Brief description of your project and its purpose]

## Tech Stack

- **Python Management**: Rye + UV for fast dependency resolution
- **Python Version**: 3.12+
- **Web Framework**: [FastAPI/Django/Flask] (if applicable)
- **Database**: [PostgreSQL/MySQL/SQLite] (if applicable)
- **Cloud Services**: [AWS/GCP/Azure] (if applicable)

## 🚀 Quick Start

### Prerequisites 前置需求

1. **Install Rye** (Modern Python project management tool)
2. **Python 3.12+**
3. **VS Code** (Recommended IDE)
4. **[Additional requirements specific to your project]**

### Quick Start (for experienced developers)

```bash
# Clone and setup
git clone <repo-url> && cd <project-name>
rye pin 3.12 && rye sync

# Configure environment
cp .env.example .env  # Edit with your credentials

# Start development server (if web app)
rye run dev

# Or run main script (if CLI app)
rye run python main.py
```

### First-time Setup Verification 首次設定驗證

After setup, run these commands to verify:
```bash
# Check if dependencies are installed
rye show

# Test if the application runs (adjust command as needed)
rye run python --version

# Check available scripts
rye run --list
```

## 📦 Complete Setup Guide

### Step 1: Install Rye (Windows)

```powershell
# Method 1: Using winget (recommended)
winget install rye

# Method 2: Direct download (if winget fails)
Invoke-WebRequest -Uri "https://github.com/astral-sh/rye/releases/latest/download/rye-installer.exe" -OutFile "rye-installer.exe"
.\rye-installer.exe

# Add Rye to PATH for current session
$env:PATH = "$env:PATH;C:\Users\$env:USERNAME\.rye\shims"
```

### Step 2: Clone and Initialize Project

```bash
# Clone repository
git clone <your-repo-url>
cd <project-name>

# Initialize Rye project (if starting fresh)
rye init --name <project-name> .

# Pin Python version
rye pin 3.12

# Install all dependencies
rye sync
```

### Step 3: Configure VS Code

**Option A: Automatic (if .vscode/settings.json exists)**
- VS Code should automatically detect the Rye virtual environment

**Option B: Manual Setup**
1. Open VS Code: `code .`
2. Press `Ctrl + Shift + P`
3. Type `Python: Select Interpreter`
4. Choose: `.venv\Scripts\python.exe` (Python 3.12.x)

**Option C: Check Current Interpreter**
- Look at VS Code status bar (bottom left)
- Should show: `Python 3.12.x ('.venv': venv)`

### Step 4: Environment Configuration

Create a `.env` file from the example:
```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your specific configuration
# Add your API keys, database URLs, etc.
```

Example `.env` contents:
```bash
# Application Configuration
APP_ENV=development
LOG_LEVEL=info

# Database (if applicable)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API Keys (if applicable)
API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here

# External Services (if applicable)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

## 🛠️ Development Commands

```bash
# Start development server (for web apps)
rye run dev

# Start production server (for web apps)
rye run start

# Run main application (for CLI apps)
rye run python main.py

# Code formatting
rye run format

# Code linting
rye run lint

# Run tests
rye run test

# Add new dependency
rye add package-name

# Add development dependency
rye add --dev package-name

# Update dependencies
rye sync

# Show project info
rye show

# Check Python version
rye run python --version

# List available scripts
rye run --list
```

## 🔧 Project Structure

```
<project-name>/
├── .python-version         # Python version (3.12.x)
├── pyproject.toml          # Dependencies and project config
├── requirements.lock       # Locked dependencies (production)
├── requirements-dev.lock   # Locked dependencies (development)
├── .env.example           # Environment variables template
├── .env                   # Environment variables (not in git)
├── .gitignore             # Git ignore file
├── README.md              # This file
├── main.py                # Main application entry point
├── src/                   # Source code directory
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── tests/             # Test files
├── data/                  # Data files (if applicable)
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

## 🚨 Troubleshooting 疑難排解

### Common Issues 常見問題

**1. Rye not found after Windows installation**
```powershell
# Manually add to PATH
$env:PATH = "$env:PATH;C:\Users\$env:USERNAME\.rye\shims"
# Or restart PowerShell/VS Code
```

**2. VS Code doesn't detect Python interpreter**
```bash
# Reload VS Code window
Ctrl + Shift + P → "Developer: Reload Window"
# Then manually select interpreter
Ctrl + Shift + P → "Python: Select Interpreter"
```

**3. Import errors when running**
```bash
# Ensure you're using Rye's Python
rye run python --version  # Should show 3.12.x
# Re-sync if needed
rye sync
```

**4. Dependencies not installing**
```bash
# Clear cache and re-sync
rye sync --force
# Or check for lock file conflicts
rm requirements.lock requirements-dev.lock
rye sync
```

## 🔍 Verification Steps

After setup, verify everything works:

```bash
# 1. Check Rye project info
rye show

# 2. Check Python version
rye run python --version

# 3. Test core imports
rye run python -c "import sys; print('Python setup OK'); print(f'Python path: {sys.executable}')"

# 4. Run application
rye run python main.py  # or whatever your main command is
```

## 🌍 Environment Variables

Required environment variables (copy to `.env`):

```bash
# Basic Configuration
APP_ENV=development
LOG_LEVEL=info

# Add your specific environment variables here
# DATABASE_URL=
# API_KEY=
# SECRET_KEY=
```

## ⚡ File Creation Timeline

Understanding how key files are created:

1. **`rye init`** → Creates basic `pyproject.toml`
2. **`rye pin 3.12`** → Creates `.python-version` (3.12.x)
3. **`rye sync`** → Creates `.venv/`, installs packages, generates lock files
4. **Manual** → Create main application files, update configurations

## 📦 Dependencies Management

This project uses Rye for modern Python dependency management:

- **Faster installs**: Uses `uv` resolver (10-100x faster than pip)
- **Lock files**: Ensures reproducible builds
- **Python version management**: Automatic Python version handling
- **Virtual environments**: Automatic venv creation and management

### Adding Dependencies

```bash
# Production dependency
rye add requests pandas numpy

# Development dependency
rye add --dev pytest black flake8

# Specific version
rye add "fastapi>=0.100.0,<1.0.0"

# From git
rye add "git+https://github.com/user/repo.git"
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit sensitive data to version control
2. **`.env` file**: Always in `.gitignore`, use `.env.example` for templates
3. **Dependencies**: Regularly update dependencies for security patches
4. **API Keys**: Use least-privilege principle for API access
5. **Input Validation**: Always validate user inputs

## 🚀 Deployment Guide

### Local Development
```bash
rye run dev  # Development with hot reload
```

### Production Deployment
```bash
# Install production dependencies only
rye sync --no-dev

# Run with production settings
APP_ENV=production rye run python main.py

# Or use production server (for web apps)
rye run start
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

# Install Rye
RUN pip install rye
RUN rye sync --no-dev

# Run application
CMD ["rye", "run", "python", "main.py"]
```

## 📊 Available Scripts

Define your scripts in `pyproject.toml`:

```toml
[tool.rye.scripts]
dev = "python main.py --dev"
start = "python main.py --prod"
test = "pytest"
format = "black ."
lint = "flake8 ."
```

## ❓ FAQ

### Q: Why use Rye instead of pip/conda?
A: Rye provides faster dependency resolution, better lock file management, and modern Python project management practices.

### Q: Can I use this with existing pip projects?
A: Yes! Run `rye init` in your existing project and `rye add` your dependencies.

### Q: How do I update Python version?
A: Use `rye pin 3.13` to update to Python 3.13, then `rye sync`.

### Q: What if Rye is not available?
A: Fall back to traditional venv: `python -m venv .venv` and `pip install -r requirements.txt`

## 📄 License

[Add your license information here]

---

## 🎯 Next Steps

After setting up this template:

1. Replace `[Project Name]` with your actual project name
2. Update the tech stack section with your specific technologies
3. Modify the project structure to match your needs
4. Add your specific environment variables to `.env.example`
5. Update the verification steps with your application-specific commands
6. Add your project-specific documentation

---

*This template is based on modern Python development practices using Rye for dependency management.*
