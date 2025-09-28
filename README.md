# Calculator

The Calculator project is a simple yet powerful command-line application that allows users to perform basic arithmetic operations such as addition, subtraction, multiplication, and division. Built with Python, it aims to provide a user-friendly interface for quick calculations.

## Features
- Perform basic arithmetic operations: addition, subtraction, multiplication, and division.
- Handle floating-point numbers and integer calculations.
- User-friendly command-line interface.
- Enhanced functionality with memory storage and scientific functions.
- Calculation history saving to a file.
- Reuse of the last result for calculations.
- Additional operations including square root, sine, cosine, tangent, and random number generation.
- Improved readability by removing unnecessary emojis from print statements.

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

Follow the prompts to enter your calculations. You can leave the input blank to reuse the last result. The history of calculations will be saved to a file named `calc_history.txt` upon exiting.

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
- **2025-09-27 17:35**: chore: remove emojis from print statements for consistency
- **2025-09-27 16:17**: feat: replace simple calculator with enhanced version
- **2025-09-27 16:15**: docs: remove outdated README.md and rename calculator.py to maiin.py
- **2025-09-27**: feat: replace simple calculator with enhanced version
  - Added new features including memory storage and scientific functions
  - Implemented calculation history saving to a file
  - Allowed reuse of last result for calculations
  - Improved user interface with additional operation options
  - Improved readability by removing unnecessary emojis from print statements
- [ ] Add future features and updates here.
