# Stock Analysis Application with Docker

This repository contains a dockerized stock analysis application that works with both ARM (Apple Silicon) and AMD64 (Intel/AMD) architectures. The setup includes MongoDB for data storage and Python scripts for stock data collection and analysis.

## Prerequisites

- Docker and Docker Compose installed
- Google Cloud Gemini API key
- Git (optional)

## Directory Structure

```
project_directory/
├── docker-compose.yml    # Docker compose configuration
├── Dockerfile           # Docker container definition
├── requirements.txt     # Python dependencies
├── run.sh              # Setup and run script
├── main.py             # Interactive Q&A application
├── stock_collector.py  # Stock data collector
└── .env                # Environment variables (created by run.sh)
```

## Initial Setup

1. Clone or create the project directory with all required files

2. Make the run script executable:
```bash
chmod +x run.sh
```

3. Run the setup script:
```bash
./run.sh
```

The script will:
- Check if Docker is running
- Create a `.env` file if it doesn't exist (you'll need to add your Gemini API key)
- Build and start the containers
- Wait for MongoDB to be ready
- Run the stock collector
- Print usage instructions

## Architecture-Specific Configuration

### For ARM (Apple Silicon) Users
No changes needed - the default configuration works out of the box.

### For AMD64 (Intel/AMD) Users

1. Edit the `Dockerfile`:
```dockerfile
# Comment out the ARM line
# FROM python:3.9-slim

# Uncomment the AMD64 line
FROM amd64/python:3.9-slim
```

2. Rebuild the containers:
```bash
docker-compose down
docker-compose up --build -d
```

## Environment Configuration

Create a `.env` file in the project root (or let `run.sh` create it for you):
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Starting the Services

1. Start all services:
```bash
docker-compose up -d
```

### Running the Applications

1. Collect stock data (non-interactive):
```bash
docker-compose exec stock_app python stock_collector.py
```

2. Run the interactive Q&A application:
```bash
docker-compose exec -it stock_app python main.py
```
Note: The `-it` flags are required for the interactive application to work properly.

### Stopping the Services

Stop all containers:
```bash
docker-compose down
```

## MongoDB Configuration

Default credentials:
- Username: admin
- Password: adminpassword
- Port: 27017

## Monitoring and Maintenance

### Viewing Logs

View all container logs:
```bash
docker-compose logs -f
```

View specific service logs:
```bash
docker-compose logs -f stock_app
docker-compose logs -f mongodb
```

### Database Management

1. Access MongoDB directly:
```bash
docker-compose exec mongodb mongosh -u admin -p adminpassword
```

2. Backup the database:
```bash
docker-compose exec mongodb mongodump --uri="mongodb://admin:adminpassword@localhost:27017" --out=/data/backup
```

### Data Persistence

- MongoDB data is stored in the `mongodb_data` Docker volume
- Application logs are stored in the `./logs` directory
- To completely reset all data:
```bash
docker-compose down -v
```

## Troubleshooting

### Common Issues

1. Interactive Application Not Working
   - Ensure you're using the `-it` flags when running main.py
   - Check if the container is running: `docker-compose ps`
   - Verify logs: `docker-compose logs stock_app`

2. MongoDB Connection Issues
   - Check if MongoDB is running: `docker-compose ps`
   - Verify MongoDB logs: `docker-compose logs mongodb`
   - Ensure credentials match in docker-compose.yml

3. Architecture-Related Issues
   - Verify you're using the correct base image in Dockerfile
   - Clean build: `docker-compose build --no-cache`
   - Check Docker architecture: `docker system info | grep Architecture`

### Container Management

Reset and rebuild everything:
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Network Configuration

- All services run on the `stock_network` Docker network
- MongoDB internal access: `mongodb:27017`
- MongoDB external access: `localhost:27017`

## Security Notes

- Change MongoDB credentials for production use
- Never commit the `.env` file to version control
- Consider using Docker secrets in production
- Application runs as non-root user inside container
- Use secure passwords in production environment

## Development

### Making Changes

After modifying source code:
1. Stop the containers: `docker-compose down`
2. Rebuild: `docker-compose up --build -d`
3. Verify changes: `docker-compose logs -f`

### Adding Dependencies

1. Add new packages to `requirements.txt`
2. Rebuild the container:
```bash
docker-compose build --no-cache stock_app
docker-compose up -d
```

## Contributing

Feel free to submit issues and pull requests for improvements.