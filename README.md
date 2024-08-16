# Nahal Kofer Environmental Monitoring System

### Website URL: [Nahal Kofer](https://nahalkofer.us.to/)

## Overview

The Nahal Kofer Environmental Monitoring System is designed to monitor and predict environmental conditions along the Kofer River. This project focuses on the integration of sensor data, flood prediction models, and data visualization tools to provide real-time insights into the river's conditions. The system allows users to access sensor data, generate QR codes for sample tracking, and view environmental data trends through a web-based interface.

## Features

- **User Authentication**: Secure user login to protect data access.
- **Flood Prediction**: Machine learning model to predict flood events based on water level, water opacity, and precipitation data.
- **Sensor Integration**: Real-time monitoring using water level, water current, and pH sensors.
- **Data Visualization**: Interactive graphs and charts displaying trends in environmental data.
- **QR Code Generation**: Generate and manage QR codes for tracking water samples.
- **Alerts**: Email alerts for potential flood conditions based on sensor data.
- **Deployment**: Deployed on AWS EC2 instance for scalability and reliability.

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (with Chart.js for data visualization)
- **Backend**: Flask (Python) for web application logic
- **Database**: SQLite for data storage, enabling easy transition to a larger database system in the future
- **Machine Learning**: TensorFlow and Keras for flood prediction models
- **Deployment**: AWS EC2 for hosting, with secure access through SSL

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ilaiazulay/Nahal-Kofer.git
   cd Nahal-Kofer
   ```

2. **Set Up the Environment**:
   - Install Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Set up the SQLite database:
     ```bash
     python manage.py db_init
     ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Website**:
   - Navigate to `http://localhost:8000` to access the website locally.

## Usage

- **Login**: Register or log in to access the dashboard.
- **Monitor**: View real-time data from the sensors and check for flood predictions.
- **Data Visualization**: Generate and view graphs for pH levels, water levels, and other environmental parameters.
- **Sample Tracking**: Use the QR code feature to track and manage water samples.

## Contact

For any inquiries, please contact [ilaiazulay](https://github.com/ilaiazulay).
