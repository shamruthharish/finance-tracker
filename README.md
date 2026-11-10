
# Finance Tracker

A simple command-line application built using Python.

## Features

- Add expenses
- Specify expense amount
- Specify expense category
- Display expense commands
- Command-line interface using argparse

## Technologies Used

- Python
- argparse
- Git
- GitHub

## How to Run

Clone the repository and open the project folder.

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the help command:

```bash
python app/main.py --help
```

Add an expense:

```bash
python app/main.py add --amount 500 --category Food
```

List expenses:

```bash
python app/main.py list
```
