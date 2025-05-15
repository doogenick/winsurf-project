# QuoteStreamLINE - Tour Operator Quote Builder

A modern web application for tour operators to create detailed quotes and itineraries.

## Features

- Multi-step quote creation form
- Dynamic activity management
- Real-time pricing calculations
- Seasonal rate adjustments
- Group discount calculations
- WETU integration for itinerary generation
- PDF/Excel export capabilities

## Setup Instructions

1. Install Python 3.8 or higher
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python setup.py
   ```

4. Run the application:
   ```
   python run.py
   ```

## Default Login Credentials

- Username: admin
- Password: admin123

## Directory Structure

```
quote_system/
├── app/
│   ├── __init__.py
│   ├── auth/
│   │   └── routes.py
│   ├── quoting/
│   │   ├── __init__.py
│   │   ├── pricing_engine.py
│   │   ├── wetu_integration.py
│   │   └── routes.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── auth/
│       ├── quoting/
│       └── layouts/
├── database/
│   ├── models.py
│   └── migrations/
├── config.py
└── run.py
```

## Usage

1. Login with the default credentials
2. Create a new quote by clicking "New Quote"
3. Fill in client details and dates
4. Add activities to the itinerary
5. Adjust the margin percentage
6. View real-time pricing updates
7. Generate PDF/Excel documents
8. Save and confirm quotes

## Development

The application uses Flask as the web framework and SQLAlchemy for database operations. The frontend is built with Bootstrap 5 and includes custom JavaScript for dynamic form handling and real-time calculations.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
