# Calculator

Calculator is a simple yet powerful command-line tool that performs basic arithmetic operations such as addition, subtraction, multiplication, and division. Built with Python, it provides a user-friendly interface for quick calculations and can be easily extended for more complex functionalities.

## Features
- Supports basic arithmetic operations: addition, subtraction, multiplication, and division.
- User-friendly command-line interface.
- Error handling for invalid inputs and division by zero.
- Extensible architecture for future enhancements.

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

Follow the on-screen prompts to perform calculations.

## Configuration
This project requires the following environment variables to be set:

- `MODEL`: Specify the model to be used for advanced calculations (if applicable).
- `OPENAI_API_KEY`: Your API key for accessing OpenAI services (if applicable).
- `SLACK_WEBHOOK_URL`: The webhook URL for sending notifications to Slack (if applicable).

## Development
To run the project locally, clone the repository and install the dependencies as described in the Installation section. Then, execute the main script:

```bash
python main.py
```

To run tests, if any are provided, use the following command:

```bash
pytest
```

For coding style standards, please adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines.

## Features / Changelog
- **2025-10-03 00:34**: feat: implement class-based calculator with enhanced features
- Placeholder for future features and changelog updates.
