### Website URL: [Nahal Kofer](https://nahalkofer.us.to/)

## Overview

The Nahal Kofer Environmental Monitoring System is designed to monitor and predict environmental conditions along the Kofer River. This project focuses on the integration of sensor data, flood prediction models, and data visualization tools to provide real-time insights into the river's conditions. The system allows users to access sensor data, generate QR codes for sample tracking, and view environmental data trends through a web-based interface.

## Note

The website contains a secret key and is restricted to use by authorized personnel only. Outsiders will not be able to register to the website. However, you can clone the repository and run the system locally on your machine.

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
   python main.py
   ```

4. **Access the Website**:
   - Navigate to `http://localhost:8000` to access the website locally.
  
## Screenshots

**Monitoring Dashboard**

![image](https://github.com/user-attachments/assets/7167f434-dc42-423b-890b-0466aa55f951)
![image](https://github.com/user-attachments/assets/5f83a5ba-ab3c-4289-aedc-43dd2a48bf32)

**Lab Tests**

![image](https://github.com/user-attachments/assets/2b3caadc-3ffa-4700-8066-bf74edd37aa9)
![image](https://github.com/user-attachments/assets/8f365ac4-7ab0-41eb-a17b-aa145cd3a895)

**QR Code Generation**

![image](https://github.com/user-attachments/assets/69631348-a278-4abf-8e02-fa7ca1caf34c)
![image](https://github.com/user-attachments/assets/601a5d3f-6140-48c0-a663-2a903fa3a80d)
![image](https://github.com/user-attachments/assets/410ccf92-78d0-43bb-bf12-c822bce22a69)
![image](https://github.com/user-attachments/assets/4c62bb57-332d-4a6a-9450-4c71dd52f508)

**Graphs**

![image](https://github.com/user-attachments/assets/46166673-3adc-4190-9f80-9cca19865aad)
![image](https://github.com/user-attachments/assets/dfb5204d-0c45-4fa1-8cf8-04548fd78890)
![image](https://github.com/user-attachments/assets/e1401d16-b120-4f96-8f86-53d18e2a5ae8)
![image](https://github.com/user-attachments/assets/796471ea-aa43-4bb8-adf2-ba34944ed324)

## Usage

- **Login**: Register or log in to access the dashboard.
- **Monitor**: View real-time data from the sensors and check for flood predictions.
- **Data Visualization**: Generate and view graphs for pH levels, water levels, and other environmental parameters.
- **Sample Tracking**: Use the QR code feature to track and manage water samples.

## Contact

For any inquiries, please contact [ilaiazulay](https://github.com/ilaiazulay).
