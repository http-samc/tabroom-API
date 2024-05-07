# Default target
all: docker-run

# Initialize Tooling
init:
	@echo "Checking Infisical"
	infisical export
	@echo "Initializing pre-commit hooks"
	cd .git/hooks && chmod +x pre-commit
	@echo "Checking Docker"
	docker
	@echo "Checking Python"
	python3 -V
	@echo "Upserting Environment"
	if [ ! -d ".venv" ]; then \
		python3 -m venv .venv; \
		case `uname` in \
			CYGWIN*|MINGW*|MSYS*) . .venv/Scripts/activate ;; \
			*) . .venv/bin/activate ;; \
		esac; \
		pip install --no-cache-dir -r requirements.txt; \
	fi
	@echo "Initialization complete!"

# Target to generate Dockerfile
dockerfile:
	@echo "Generating Dockerfile..."
	python3 bin/scripts/generate_dockerfile.py

# Target to build Docker Image
docker-build:
	make dockerfile
	@echo "Building Docker Image"
	infisical run --env=prod -- docker build -t backend .

# Target to start a new Docker container with the latest Image
docker-run:
	make docker-build
	@echo "Running Docker"
	docker run backend .

# List all targets as PHONY
.PHONY: all init dockerfile docker-build docker-run
