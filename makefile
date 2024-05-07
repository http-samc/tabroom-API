# Default target
all: dockerfile

# Target to generate Dockerfile
dockerfile:
	@echo "Generating Dockerfile..."
	@python3 bin/scripts/generate_dockerfile.py

# Initialize Pre-Commit
init:
	@echo "Checking Infisical"
	@echo
	infisical export
	@echo
	@echo "Initializing pre-commit hooks"
	cd .git/hooks && chmod +x pre-commit
	@echo
	@echo "Initialization complete!"

.PHONY: all dockerfile
