# Calculator

The Calculator project is a simple yet powerful command-line application that allows users to perform basic arithmetic operations such as addition, subtraction, multiplication, and division. Built with Python, it aims to provide a user-friendly interface for quick calculations.

## Features
- Perform basic arithmetic operations: addition, subtraction, multiplication, and division.
- Handle floating-point numbers and integer calculations.
- User-friendly command-line interface.

## Installation
To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage
To run the project, execute the following command in your terminal:

```bash
python main.py
```

Follow the prompts to enter your calculations.

## Configuration
This project requires the following environment variables to be set:

- `MODEL`: Specify the model to be used for advanced calculations (if applicable).
- `OPENAI_API_KEY`: Your API key for accessing OpenAI services (if applicable).
- `SLACK_WEBHOOK_URL`: URL for sending notifications to Slack (if applicable).

## Development
- To run the project locally, ensure you have Python installed and follow the Installation steps above.
- To run tests, use the following command:

```bash
pytest
```

- This project adheres to PEP 8 coding style standards. Please ensure your code follows these guidelines for consistency.

## Features / Changelog
- **2025-09-27 16:15**: docs: remove outdated README.md and rename calculator.py to maiin.py
- [ ] Add future features and updates here.
