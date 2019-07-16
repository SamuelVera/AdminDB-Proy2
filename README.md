# Data Analysis for a Simulated Smart Shopping Center
# Project Structure
This project consists of the following:
- 3 Transactional databases and a Datawarehouse managed with PostgreSQL. The backup files are inside the folder "Backups de las DBs"
- A data generation algorithm named "randomDataScript.py" that simulates the data capture of sensors like cameras, beacons and table sensors and sends it with the MQTT Protocol to a subscription algorithm named "subscriber.py", both programmed in Python. The files are inside the "Algoritmos de generación de datos" folder
- Data Integration flows made with Pentaho Data Integration that transforms the data from the Transactional Databases to an OLAP model and stores it in the Datawarehouse. The flows are in the folder "Flujos de Pentaho DI"
- A Linear Regression made with scikit-learn with the cloud tool Colaboratory to predict the quantity of people that enters the shopping center. Hosted here: https://colab.research.google.com/drive/1031wli52Ee3CtaP4lDbHAQhiYanEwBkO?authuser=1#scrollTo=HOE0e8ybjIDV
- Qlik Sense Reports of sellings and person flows through shops and the Shopping Center. File in the folder "Reportes Qlik Sense"

# Estructura del Proyecto
- 3 Bases de Datos Transaccionales y un Datawarehouse manejados con PostgreSQL. Los backups de las DBs están en la carpeta "Backups de las DBs".
- Un algoritmo de generación de datos llamado "randomDataScript.py" que simula la captura de datos de sensores de mesa, cámaras y beacons y envía dichos datos mediante el protocolo MQTT a un algoritmo de subscripción llamado "subscriber.py", ambos algoritmos han sido programados con Python. Los archivos están en l carpeta "Algoritmos de generación de datos".
- Flujos de integración de datos hechos con Pentaho Data Integration, transforman la data de las Bases de Datos Transaccionales a un modelo de cubos OLAP y almacena la data transformada en un Datawarehouse. Los archivos se encuentran en la carpeta "Flujos de Pentaho DI".
- Una Regresión Lineal hecha con scikit-learn en la herramienta Colaboratory para predecir la cantidad de gente que entra y sale del Centro Comercial. El archivo está hosteado en: https://colab.research.google.com/drive/1031wli52Ee3CtaP4lDbHAQhiYanEwBkO?authuser=1#scrollTo=HOE0e8ybjIDV
- Reportes sobre ventas y flujo de pesonas a través de tiendas y el centro comercial hechos en Qlik Sense. Los archivos están en la carpeta "Reportes Qlik Sense".
