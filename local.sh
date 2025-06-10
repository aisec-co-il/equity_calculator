#!/bin/bash

# .env file (or set manually)
DOCKER_BUILD_CONTEXT=./  # Build from current directory
FLASK_ENV=development    # Enable debug mode

# Start the service
docker-compose up