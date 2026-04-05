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