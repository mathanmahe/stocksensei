#!/bin/bash

# Check if .env file exists, if not create it
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "GEMINI_API_KEY=your_api_key_here" > .env
    echo "Please edit .env file and add your Gemini API key"
    exit 1
fi

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check Docker status
check_docker

# Build and start the containers
echo "Building and starting containers..."
docker-compose up --build -d

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
sleep 10

# Run the stock collector
echo "Running stock collector..."
docker-compose exec stock_app python stock_collector.py

# Print instructions
echo "
Setup completed!

To use the application:
1. Run the interactive Q&A application:
   docker-compose exec -it stock_app python main.py

2. To update stock data later:
   docker-compose exec stock_app python stock_collector.py

3. To stop all containers:
   docker-compose down

4. To view logs:
   docker-compose logs -f

Note: Data is persisted in a Docker volume. To completely reset:
   docker-compose down -v
"