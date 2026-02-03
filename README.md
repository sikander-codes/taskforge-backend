# TaskForge

This is the source code for **TaskForge** — a project task management tool. It manages projects, tasks, and workflows. The project is in initial setup; the folder structure is in place and development will proceed step by step.

For more details, see the sections below.

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Contributing](#contributing)

## Getting Started

Follow the instructions below to set up and run TaskForge.

## Prerequisites

Ensure you have the following installed:

- Python >= 3.10
- PostgreSQL

## Project Setup

Clone the project repository:

```bash
git clone https://github.com/sikander-codes/taskforge-backend.git
cd taskforge-backend
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
env\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Set up environment variables by copying the example configuration:

```bash
cp .env.example .env
```

Run database migrations to initialize the database schema:

```bash
alembic upgrade head
```

## Running the Application

Start the application:

```bash
uvicorn app.main:app --reload
```

## Running Tests

Run the tests using this command:

```bash
pytest
```

## Contributing

Contributions are welcome. Please open an issue or submit a pull request.
