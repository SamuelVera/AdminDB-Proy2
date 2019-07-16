# Data Analysis for a Simulated Smart Shopping Center
# Project Structure
This project consists of the following:
- 3 Transactional databases and a Datawarehouse managed with PostgreSQL. The backup files are inside the folder "Backups de las DBs"
- A data generation algorithm named "randomDataScript.py" that simulates the data capture of sensors like cameras, beacons and table sensors and sends it with the MQTT Protocol to a subscription algorithm named "subscriber.py", both programmed in Python. The files are inside the "Algoritmos de generación de datos" folder
- Data Integration flows made with Pentaho Data Integration that transforms the data from the OLTP Databases to an OLAP model and stores it in the Datawarehouse. The flows are in the folder "Flujos de Pentaho DI"
- A Linear Regression made with scikit-learn with the cloud tool Colaboratory to predict the quantity of people that enters the shopping center. Hosted here: https://colab.research.google.com/drive/1031wli52Ee3CtaP4lDbHAQhiYanEwBkO?authuser=1#scrollTo=HOE0e8ybjIDV
- Qlik Sense Reports of sellings and person flows through shops and the Shopping Center. File in the folder "Reportes Qlik Sense"
