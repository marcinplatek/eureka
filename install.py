import os
import subprocess
import venv


def main():
    # Set the working directory
    work_dir = os.path.expanduser("~/.eureka")

    # Determine the current repository path
    repo_path = os.path.dirname(os.path.abspath(__file__))

    # Create a Python virtual environment
    venv_dir = os.path.join(work_dir, "venv")
    venv.create(venv_dir, with_pip=True)

    # Install the local package and its dependencies
    pip_path = os.path.join(venv_dir, "bin", "pip")
    subprocess.run([pip_path, "install", repo_path])

    shell_config = os.path.expanduser("~/.bashrc")
    shell = os.environ.get("SHELL")

    if shell:
        if "zsh" in shell:
            shell_config = os.path.expanduser("~/.zshrc")
            print("Configured zsh")
        elif "bash" in shell:
            shell_config = os.path.expanduser("~/.bashrc")
            print("Configured bash")
    else:
        print("Unknown shell")

    # Read the shell configuration file
    with open(shell_config, "r") as f:
        content = f.read()

    # Check if the PATH update command is already present
    bin_path = os.path.join("${HOME}/.eureka/venv/bin")
    path_update = f'export PATH="{bin_path}:$PATH"'

    if path_update not in content:
        # Add the PATH update command if it's not present
        with open(shell_config, "a") as f:
            f.write(f"\n{path_update}\n")
        print(f"Added Eureka to the PATH variable in {shell_config}.")
    else:
        print(f"Eureka is already in the PATH variable in {shell_config}.")


if __name__ == "__main__":
    main()
