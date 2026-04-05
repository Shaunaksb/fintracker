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
    parser.add_argument("--stage-two", action="store_true", help=argparse.SUPPRESS) # Internal use only
    args = parser.parse_args()

    # Determine which manager to use
    if args.uv:
        manager = "uv"
    elif args.pip:
        manager = "pip"
    else:
        # Auto-detect uv
        if shutil.which("uv"):
            manager = "uv"
        else:
            manager = "pip"

    # Stage One: Installation and Relaunch
    if not args.stage_two:
        if manager == "uv":
            print(">>> [Stage 1] Installing dependencies using uv...")
            subprocess.check_call(["uv", "sync"])
            print(">>> Relaunching script in virtual environment...")
            relaunch_cmd = ["uv", "run", "python", "install.py", "--stage-two"]
        else:
            print(">>> [Stage 1] Installing dependencies using pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print(">>> Relaunching script...")
            relaunch_cmd = [sys.executable, "install.py", "--stage-two"]

        # Forward flags
        if args.uv: relaunch_cmd.append("--uv")
        if args.pip: relaunch_cmd.append("--pip")
        if args.no_input: relaunch_cmd.append("--no-input")

        sys.exit(subprocess.call(relaunch_cmd))

    # Stage Two: Configuration and Setup
    print(">>> [Stage 2] Configuration and Database Setup")
    python_exec = [sys.executable] # Since we're already in the target environment (via uv run or pip relaunch)

    # Generate a secret key for the Django project
    import dotenv
    dotenv_file = dotenv.find_dotenv()
    if not dotenv_file:
        with open(".env", "w") as f:
            f.write("")
        dotenv_file = ".env"
    
    dotenv.load_dotenv(dotenv_file)

    from django.core.management.utils import get_random_secret_key
    scrt = get_random_secret_key()
    dotenv.set_key(dotenv_file, 'SECRET_KEY', scrt)
    print(">>> Generated and saved a new SECRET_KEY to .env")

    super_user_creds = {}

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
            ("DB_PORT", "5432"),
            # Superuser credentials
            ("DJANGO_SUPERUSER_USERNAME", "admin"),
            ("DJANGO_SUPERUSER_EMAIL", "admin@localhost"),
            ("DJANGO_SUPERUSER_PASSWORD", "password123"),
        ]

        for key, default in env_vars:
            current = dotenv.get_key(dotenv_file, key)
            prompt_val = current if current else default
            try:
                val = input(f" - {key} [{prompt_val}]: ").strip()
                if not val:
                    val = prompt_val
                dotenv.set_key(dotenv_file, key, val)
                if key.startswith("DJANGO_SUPERUSER_"):
                    super_user_creds[key] = val
            except EOFError:
                break
        print(">>> Environment variables updated.")

    # Migrate the database
    print(">>> Running migrations...")
    subprocess.check_call(python_exec + ["manage.py", "makemigrations"])
    subprocess.check_call(python_exec + ["manage.py", "migrate"])

    # Create a superuser
    print(">>> Creating superuser...")
    try:
        # Use credentials from interactive phase or current .env
        env = os.environ.copy()
        for key in ["DJANGO_SUPERUSER_USERNAME", "DJANGO_SUPERUSER_EMAIL", "DJANGO_SUPERUSER_PASSWORD"]:
            val = super_user_creds.get(key) or dotenv.get_key(dotenv_file, key)
            if val:
                env[key] = val
        
        subprocess.check_call(python_exec + ["manage.py", "createsuperuser", "--noinput"], env=env)
    except subprocess.CalledProcessError as e:
        print(f"Note: Superuser creation failed or already exists. Error: {e}")

    # Run the server
    print(">>> Starting the development server...")
    subprocess.check_call(python_exec + ["manage.py", "runserver"])


if __name__ == "__main__":
    main()