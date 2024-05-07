# Default target
all: dockerfile

# Target to generate Dockerfile
dockerfile:
	@echo "Generating Dockerfile..."
	@python3 bin/scripts/generate_dockerfile.py

.PHONY: all dockerfile
