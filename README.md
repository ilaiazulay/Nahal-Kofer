# Payroll Calculator for Hi-Tech Company

**Note: This is an early stage built. The application is currently in the testing phase and is tailored specifically to meet the unique requirements of a hi-tech company. It is not intended for general use and may not be suitable for applications outside of the specified conditions.**

## Overview

This Python project is a payroll calculator designed to meet the custom needs of a specific hi-tech company. It utilizes Flask for the web framework, SQLite for data storage, and includes various conditions and variables for accurate payroll calculations.

## Prerequisites

Before using this payroll calculator, ensure you have the following dependencies installed:

- Python 3.x
- Flask
- SQLite

You can install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Installation
1. Clone the repository:

```bash
git clone https://github.com/your-username/your-project.git
```

2. Change into the project directory:

```bash
cd your-project
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

## Configuration
To configure the project for your specific needs:

- Set up the database by running any necessary migration scripts.
- Adjust environment variables or configuration files as needed.
  
## Usage

### Sign Up / Login:
- Upon first use, sign up using your email and password.
- Log in with your credentials if you already have an account.
### Home Screen:
- View all the shifts associated with your account.
- Add new shifts or delete existing ones.
### Calculate Salary:
- Navigate to the "Calculate Salary" page to compute your salary for a specific time period.
- The calculator follows the hi-tech company's rules for salary calculations.

## Database
This project uses SQLite for data storage. Be sure to check and configure the database connections as needed.
