# Rick and Morty AI Agent

![app screenshot](resources/gameplay.png)
This project implements an AI-powered chat agent based on Rick from Rick and Morty, with memory management, reflection capabilities, and multimedia generation.

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.7+
- Homebrew (for macOS users)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/albertaleksieiev/RickAndMortyAIAgent
   cd RickAndMortyAIAgent
   ```

2. Install required packages using pip:
   ```
   pip install anthropic openai fakeyou playsound requests python-dotenv
   ```

3. Install additional dependencies using Homebrew (for macOS users):
   ```
   brew install catimg
   ```
**Note: On some Macs, there might be an issue displaying images in zsh. Using iTerm2 as your terminal emulator can resolve this issue.**

## Configuration

1. Set up your environment variables:
   - Copy the `example.env` file to `.env` in the project root directory
   - Edit the `.env` file and add your API keys and credentials:
     ```
     ANTHROPIC_API_KEY=your_anthropic_api_key
     OPENAI_API_KEY=your_openai_api_key
     FAKEYOU_EMAIL=your_fakeyou_email@example.com
     FAKEYOU_PASSWORD=your_fakeyou_password
     ```

## Usage

Run the main script to start the chat:

```
python index.py
```

Follow the on-screen prompts to interact with the Rick AI chat agent.

## Features

- Conversational AI using Anthropic's Claude model, personified as Rick from Rick and Morty
- Memory management for factual and emotional information
- Reflection capabilities for conversation analysis
- Image generation using DALL-E
- Text-to-speech synthesis using FakeYou
- SQLite database for persistent storage

## Project Structure

- `index.py`: Main entry point and chat loop
- `DatabaseHandler.py`: Manages SQLite database operations
- `MemoryManager.py`: Handles memory storage and retrieval
- `FriendAgent.py`: Implements the main chat agent functionality
- `ReflectionAgent.py`: Provides reflection and analysis capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
