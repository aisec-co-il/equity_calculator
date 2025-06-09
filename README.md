# Startup Equity Calculator

A web application for calculating startup equity distribution, funding rounds, and exit proceeds.

## Features

- Calculate initial equity distribution among founders
- Track dilution through funding rounds (Seed, Series A)
- Calculate exit proceeds with tax considerations
- Support for Israeli tax rates (25% for individuals, 23% for companies)
- Interactive sliders for percentage inputs
- Real-time validation of equity distribution

## Setup

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd startup-equity-calculator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:4000

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t startup-equity-calculator .
```

2. Run the container:
```bash
docker run -p 4000:4000 startup-equity-calculator
```

The application will be available at http://localhost:4000

## Usage

1. Enter the total number of shares
2. Set founder equity percentages using sliders
3. Set options pool percentage
4. Enter funding round details (amount and valuation)
5. Set exit amount and tax type
6. Click "Calculate" to see the results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 