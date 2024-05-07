import subprocess

def get_env_variables():
    # Run the infisical export command and capture its output
    result = subprocess.run(['infisical', 'export', '--env=prod'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to execute command:", result.stderr)
        return None

    # Parse the .env output to extract variables
    variables = {}
    for line in result.stdout.splitlines():
        key, _, value = line.partition('=')
        variables[key.strip()] = value.strip()
    return variables

def generate_dockerfile(variables):
    # Basic Dockerfile content
    dockerfile_content = [
        "# Official Python image",
        "FROM python:3.11.4-slim",
        "",
        "# Set the working directory in the container",
        "WORKDIR /usr/src/app",
        "",
        "# Copy the current directory contents into container",
        "COPY . .",
        "",
        "# Arguments"
    ]

    # Append ARG lines for each variable
    arg_lines = [f"ARG {var}" for var in variables]
    dockerfile_content.extend(arg_lines)

    # Append ENV lines for each variable, in a separate block
    dockerfile_content.append("\n# Environment Variables")
    env_lines = [f"ENV {var}=${{{var}}}" for var in variables]
    dockerfile_content.extend(env_lines)

    # Additional Dockerfile commands
    dockerfile_content.extend([
        "",
        "# Install from requirements.txt",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "",
        "# Start the program",
        'ENTRYPOINT ["python", "main.py"]'
    ])

    # Write to Dockerfile
    with open('Dockerfile', 'w') as f:
        f.write('\n'.join(dockerfile_content))
    print("Dockerfile generated successfully.")

def main():
    variables = get_env_variables()
    if variables is not None:
        generate_dockerfile(variables)

if __name__ == "__main__":
    main()