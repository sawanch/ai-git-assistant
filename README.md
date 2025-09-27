# 16-GenAI-Project
The 16-GenAI-Project is a Python-based application designed to leverage generative AI for enhanced productivity and collaboration. It integrates with popular platforms to streamline workflows and improve communication, making it an essential tool for teams looking to harness the power of AI.

## Features
- AI-driven assistance for project management tasks
- Integration with Slack for real-time updates
- Customizable model settings for tailored responses
- User-friendly command-line interface

## Installation
To set up the project, run the following command:
```
pip install -r requirements.txt
```

## Usage
To run the application, use the command:
```
python ai_git_assistant.py
```
Flags:
- `--help`: Displays help information about command usage.

## Configuration
The following environment variables are required:
- `MODEL`: Specifies the AI model to use.
- `OPENAI_API_KEY`: Your API key for accessing OpenAI services.
- `SLACK_WEBHOOK_URL`: The webhook URL for sending messages to Slack.

## Development
- To run the application locally, ensure all dependencies are installed and execute `python ai_git_assistant.py`.
- To run tests, use the command `pytest` in the project directory.
- Follow PEP 8 coding standards for consistent code style and readability.

## Features / Changelog
- **2025-09-27 15:58**: feat: add simple calculator with multiple operations
- **2025-09-27 15:55**: docs: remove outdated README file
- Initial release of the 16-GenAI-Project.
