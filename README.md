# Calculator

The Calculator project is a simple yet powerful command-line application built in Python that allows users to perform basic arithmetic operations such as addition, subtraction, multiplication, and division. It is designed to be user-friendly and efficient, making it a great tool for quick calculations.

## Features
- Perform basic arithmetic operations: addition, subtraction, multiplication, and division.
- User-friendly command-line interface.
- Error handling for invalid inputs and division by zero.

## Installation
To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage
To run the project, use the following command in your terminal:

```bash
python main.py
```

Follow the prompts to enter your calculations.

## Configuration
This project requires the following environment variables if you plan to extend its functionality:

- `MODEL`: Specify the model to be used for advanced calculations (if applicable).
- `OPENAI_API_KEY`: Your API key for accessing OpenAI services (if applicable).
- `SLACK_WEBHOOK_URL`: URL for sending notifications to Slack (if applicable).

## Development
- To run the project locally, clone the repository and install the dependencies as described in the Installation section.
- To run tests, execute the following command:

```bash
pytest
```

- Follow PEP 8 coding style standards for Python code to maintain readability and consistency.

## Features / Changelog
- **2025-10-03 13:11**: feat: add unit conversion feature to calculator
- Placeholder for future features and changelog updates.
