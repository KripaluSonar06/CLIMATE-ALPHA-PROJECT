"""
Setup script for Climate-Alpha platform
"""

import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    print("Creating directory structure...")
    
    directories = [
        "data/raw",
        "data/processed",
        "data/results",
        "logs",
        "models/saved_models",
        "backend/api/routes",
        "backend/models",
        "backend/strategies",
        "backend/risk",
        "backend/data",
        "backend/utils"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print("✓ Directory structure created\n")


def create_env_file():
    """Create .env file from template"""
    print("Setting up environment file...")
    
    env_example = Path("config/.env.example")
    env_file = Path("config/.env")
    
    if env_file.exists():
        print("  ⚠ .env file already exists, skipping")
    else:
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("  ✓ Created .env from template")
            print("  ⚠ Please edit config/.env with your API keys")
        else:
            print("  ✗ .env.example not found")
    
    print()


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"  ✗ Python 3.9+ required, found {version.major}.{version.minor}")
        sys.exit(1)
    
    print()


def install_requirements():
    """Install Python requirements"""
    print("Installing Python packages...")
    print("  (This may take several minutes)")
    
    import subprocess
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True
        )
        print("  ✓ All packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error installing packages: {e}")
        print("  Please run manually: pip install -r requirements.txt")
    
    print()


def create_readme_files():
    """Create placeholder README files"""
    print("Creating README files...")
    
    readme_paths = [
        "backend/README.md",
        "notebooks/README.md",
        "docs/README.md"
    ]
    
    content = {
        "backend/README.md": "# Backend\n\nBackend code for Climate-Alpha platform.\n",
        "notebooks/README.md": "# Notebooks\n\nJupyter notebooks for analysis and demonstrations.\n",
        "docs/README.md": "# Documentation\n\nDetailed documentation for the platform.\n"
    }
    
    for path in readme_paths:
        readme_file = Path(path)
        if not readme_file.exists():
            readme_file.write_text(content.get(path, "# README\n"))
            print(f"  ✓ {path}")
    
    print()


def initialize_git():
    """Initialize git repository"""
    print("Initializing git repository...")
    
    import subprocess
    
    if Path(".git").exists():
        print("  ⚠ Git repository already initialized")
    else:
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: Climate-Alpha project"],
                check=True,
                capture_output=True
            )
            print("  ✓ Git repository initialized")
        except subprocess.CalledProcessError:
            print("  ⚠ Git not available or error initializing")
    
    print()


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("CLIMATE-ALPHA SETUP")
    print("Quantitative ESG Trading Platform")
    print("="*60 + "\n")
    
    check_python_version()
    create_directories()
    create_env_file()
    create_readme_files()
    
    # Ask if user wants to install packages
    response = input("Install Python packages? (y/n): ").lower()
    if response == 'y':
        install_requirements()
    else:
        print("\nSkipping package installation")
        print("Run manually: pip install -r requirements.txt\n")
    
    # Ask about git
    response = input("Initialize git repository? (y/n): ").lower()
    if response == 'y':
        initialize_git()
    
    print("="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit config/.env with your API keys")
    print("2. Run: python scripts/download_data.py")
    print("3. Explore: jupyter notebook notebooks/")
    print("4. Start API: cd backend && uvicorn api.main:app --reload")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
