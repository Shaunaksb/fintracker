# Install script to install the required packages and to generate a secret key for the Django project.
import os
import subprocess
import sys
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description="Install and setup the Django project.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--uv", action="store_true", help="Use 'uv' for package management.")
    group.add_argument("--pip", action="store_true", help="Use 'pip' for package management.")
    parser.add_argument("--no-input", action="store_true", help="Skip interactive environment configuration.")
    args = parser.parse_args()

    # Determine which manager to use
    if args.uv:
        manager = "uv"
    elif args.pip:
        manager = "pip"
    else:
        # Auto-detect uv
        if shutil.which("uv"):
            print("Detected 'uv', using it for installation.")
            manager = "uv"
        else:
            print("'uv' not found, defaulting to 'pip'.")
            manager = "pip"

    # Install required packages
    if manager == "uv":
        print(">>> Installing dependencies using uv...")
        subprocess.check_call(["uv", "sync"])
        python_exec = ["uv", "run", "python"]
    else:
        print(">>> Installing dependencies using pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        python_exec = [sys.executable]

    # Generate a secret key for the Django project
    # Importing here because these packages are installed above
    import dotenv
    dotenv_file = dotenv.find_dotenv()
    if not dotenv_file:
        # Create .env if it doesn't exist
        with open(".env", "w") as f:
            f.write("")
        dotenv_file = ".env"
    
    dotenv.load_dotenv(dotenv_file)

    from django.core.management.utils import get_random_secret_key
    scrt = get_random_secret_key()
    dotenv.set_key(dotenv_file, 'SECRET_KEY', scrt)
    print(">>> Generated and saved a new SECRET_KEY to .env")

    # Interactive setup for other env variables
    if not args.no_input:
        print("\n>>> Interactive Environment Configuration")
        print("Enter values or press ENTER to keep the default/existing value.")
        
        env_vars = [
            ("DEBUG", "True"),
            ("ALLOWED_HOSTS", "localhost,127.0.0.1"),
            ("DB_ENGINE", "django.db.backends.postgresql"),
            ("DB_NAME", "fintracker"),
            ("DB_USER", "your-db-username"),
            ("DB_PASSWORD", "your-db-password"),
            ("DB_HOST", "localhost"),
            ("DB_PORT", "5432")
        ]

        for key, default in env_vars:
            current = dotenv.get_key(dotenv_file, key)
            prompt_val = current if current else default
            try:
                val = input(f" - {key} [{prompt_val}]: ").strip()
                if not val:
                    val = prompt_val
                dotenv.set_key(dotenv_file, key, val)
            except EOFError:
                break
        print(">>> Environment variables updated.")

    # Migrate the database
    print(">>> Running migrations...")
    subprocess.check_call(python_exec + ["manage.py", "makemigrations"])
    subprocess.check_call(python_exec + ["manage.py", "migrate"])

    # Create a superuser
    print(">>> Creating superuser (if not already exists)...")
    try:
        subprocess.check_call(python_exec + ["manage.py", "createsuperuser", "--noinput"])
    except subprocess.CalledProcessError:
        print("Note: Superuser creation failed or already exists.")

    # Run the server
    print(">>> Starting the development server...")
    subprocess.check_call(python_exec + ["manage.py", "runserver"])

if __name__ == "__main__":
    main()