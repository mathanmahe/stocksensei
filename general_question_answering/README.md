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


Here’s a short `README.md` file based on your steps:

---

# Data Loading for SEC Filings

This guide provides instructions for loading SEC filings data into MongoDB within the `stock_app` container.

The SEC-filings textual data is contained in the `./general_question_answering/data` folder:

## Steps

### 1. Set Permissions for the Data Folder
Ensure that the `data` folder has the necessary read permissions:

```bash
chmod -R 755 data
```

### 2. Mount the Data Folder in Docker
Verify that the `data` folder is properly mounted in `docker-compose.yml` under `stock_app`:

```yaml
stock_app:
  build: 
    context: .
    dockerfile: Dockerfile
  environment:
    - MONGODB_URI=mongodb://admin:adminpassword@mongodb:27017/
    - GEMINI_API_KEY=${GEMINI_API_KEY}
    - PYTHONUNBUFFERED=1
  volumes:
    - ./logs:/app/logs
    - ./data:/data:rw
```
### 3. Stop the containers: 
```docker-compose down```

### 4. Rebuild the containers:
```docker-compose up --build -d```


### 5. Load Data into MongoDB
Run the following command to load SEC filings into MongoDB:

```
docker-compose exec stock_app python load_data_into_mongodb.py
```

### Success
The SEC filings data will now be loaded into the `sec_data` database, within a collection named `filings`.

---

This `README.md` provides a quick reference to ensure the data is successfully loaded into MongoDB!


## Description of SEC-Filings dataset

Example MetaData:

This dataset contains structured JSON files representing the annual 10-K filings of companies in the NASDAQ-100 index over five years (2020-2024). Each JSON file corresponds to a single 10-K filing, providing both qualitative and quantitative information about each company's business, financial health, and operational risks.

Content Overview
Each JSON file includes the following main sections, structured as keys:
Item 1. Business
Item 1A. Risk Factors
Item 1B. Unresolved Staff Comments
Item 2. Properties
Item 3. Legal Proceedings
Item 4. Mine Safety Disclosures
Item 5. Market for Registrant’s Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities
Item 6. Selected Financial Data
Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations
Item 7A. Quantitative and Qualitative Disclosures About Market Risk
Item 8. Financial Statements and Supplementary Data
Item 9. Changes in and Disagreements With Accountants on Accounting and Financial Disclosure
Item 9A. Controls and Procedures
Item 10. Directors and Executive Officers of the Registrant
Item 11. Executive Compensation
Item 12. Security Ownership of Certain Beneficial Owners and Management
Item 13. Certain Relationships and Related Transactions
Item 14. Principal Accountant Fees and Services
Item 15. Exhibits, Financial Statement Schedules
Item 16. Form 10-K Summary

Here is an example of what the data file might look like. 

```
{
  "cik": "320193",
  "company": "Apple Inc.",
  "filing_type": "10-K",
  "filing_date": "2022-10-28",
  "period_of_report": "2022-09-24",
  "sic": "3571",
  "state_of_inc": "CA",
  "state_location": "CA",
  "fiscal_year_end": "0924",
  "filing_html_index": "https://www.sec.gov/Archives/edgar/data/320193/0000320193-22-000108-index.html",
  "htm_filing_link": "https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm",
  "complete_text_filing_link": "https://www.sec.gov/Archives/edgar/data/320193/0000320193-22-000108.txt",
  "filename": "320193_10K_2022_0000320193-22-000108.htm",
  "item_1": "Item 1. Business\nCompany Background\nThe Company designs, manufactures ...",
  "item_1A": "Item 1A. Risk Factors\nThe Company’s business, reputation, results of ...",
  "item_1B": "Item 1B. Unresolved Staff Comments\nNone.",
  "item_1C": "",
  "item_2": "Item 2. Properties\nThe Company’s headquarters are located in Cupertino, California. ...",
  "item_3": "Item 3. Legal Proceedings\nEpic Games\nEpic Games, Inc. (“Epic”) filed a lawsuit ...",
  "item_4": "Item 4. Mine Safety Disclosures\nNot applicable. ...",
  "item_5": "Item 5. Market for Registrant’s Common Equity, Related Stockholder ...",
  "item_6": "Item 6. [Reserved]\nApple Inc. | 2022 Form 10-K | 19",
  "item_7": "Item 7. Management’s Discussion and Analysis of Financial Condition ...",
  "item_8": "Item 8. Financial Statements and Supplementary Data\nAll financial ...",
  "item_9": "Item 9. Changes in and Disagreements with Accountants on Accounting and Financial Disclosure\nNone.",
  "item_9A": "Item 9A. Controls and Procedures\nEvaluation of Disclosure Controls and ...",
  "item_9B": "Item 9B. Other Information\nRule 10b5-1 Trading Plans\nDuring the three months ...",
  "item_9C": "Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections\nNot applicable. ...",
  "item_10": "Item 10. Directors, Executive Officers and Corporate Governance\nThe information required ...",
  "item_11": "Item 11. Executive Compensation\nThe information required by this Item will be included ...",
  "item_12": "Item 12. Security Ownership of Certain Beneficial Owners and Management and ...",
  "item_13": "Item 13. Certain Relationships and Related Transactions, and Director Independence ...",
  "item_14": "Item 14. Principal Accountant Fees and Services\nThe information required ...",
  "item_15": "Item 15. Exhibit and Financial Statement Schedules\n(a)Documents filed as part ...",
  "item_16": "Item 16. Form 10-K Summary\nNone.\nApple Inc. | 2022 Form 10-K | 57",
  "filename": "320193_10K_2018_0000320193-18-000145.htm",
  "stock_ticker": "AAPL"
}
```