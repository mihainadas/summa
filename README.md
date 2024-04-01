# Project Summa

Project Summa is an LLM-based text processing system built with Python and Django. It provides a modular and scalable solution for various text processing tasks.

## Features

- **Core Application**: Contains the main business logic of the system, including Django models for handling data related to text processing.
- **Galandriel Application**: The main application of the project, containing the settings, URL configurations, and WSGI and ASGI applications for deployment.
- **Summa Module**: A custom library for text processing, including classes for text preprocessing, processing, language model management, evaluation, and pipeline running.
- **Dockerized**: The project is Dockerized for easy deployment and scaling.
- **VS Code Configurations**: Includes configurations for running and debugging the Django server and the `summa-cli.py` script in Visual Studio Code.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8 or higher
- Docker
- Docker Compose

### Installation

1. Clone the repository: `git clone https://github.com/mihainadas/summa.git`
2. Navigate to the project directory: `cd summa`
3. Build the Docker image: `docker-compose build`
4. Run the Docker container: `docker-compose up`

## License

This project is licensed under the MIT License.
