#!/bin/bash

# Script to run the build inside a Docker container

IMAGE_NAME="productivity-tracker-builder"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: 'docker' command not found."
    echo "To install Docker on Ubuntu/Debian, run:"
    echo "  sudo apt-get update && sudo apt-get install docker.io"
    echo "Alternatively, you can use the local build script (no Docker required):"
    echo "  bash build.sh"
    exit 1
fi

# Define docker command (detect if sudo is needed)
DOCKER_CMD="docker"
if ! docker info >/dev/null 2>&1; then
    if command -v sudo >/dev/null 2>&1; then
        DOCKER_CMD="sudo docker"
        echo "Note: Using 'sudo' for Docker commands as the current user doesn't have permissions."
    else
        echo "Error: Docker permission denied and 'sudo' not found."
        echo "Please add your user to the 'docker' group: sudo usermod -aG docker $USER"
        exit 1
    fi
fi

echo "Building Docker image..."
$DOCKER_CMD build -t $IMAGE_NAME -f Dockerfile.build .

if [ $? -ne 0 ]; then
    echo "Docker image build failed."
    exit 1
fi

echo "Running build inside Docker container..."
# We mount the current directory to /app in the container
# This allows the container to read the source and write the output packages back to the host
$DOCKER_CMD run --rm \
    -v "$(pwd)":/app \
    -e DOCKER_BUILD=1 \
    $IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "Containerized build failed."
    exit 1
fi

echo "Containerized build successful! Packages should be in the current directory."
