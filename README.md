The AI-Driven Healthcare Anomaly Detection System is an end-to-end real-time monitoring and decision-support platform designed to detect abnormal patterns in patient vital signs and generate early health risk alerts. Unlike traditional healthcare monitoring systems that rely on static thresholds or post-incident analysis, this system continuously analyzes live physiological data streams using machine learning models to identify anomalies as they occur.

The system ingests real-time patient vitals such as heart rate, oxygen saturation (SpO₂), body temperature, and blood pressure through a streaming pipeline powered by Apache Kafka. These vitals are processed by advanced anomaly detection models, including an Autoencoder Neural Network and Isolation Forest, which compute anomaly scores and classify patient conditions into severity levels such as LOW, MEDIUM, and HIGH.

Detected anomalies are stored in a PostgreSQL database, visualized on an interactive Flask-based dashboard, and critical alerts automatically trigger email notifications to healthcare administrators. The project demonstrates the practical application of machine learning, real-time data streaming, backend APIs, and dashboard visualization in solving real-world healthcare monitoring challenges.

TO START THE PROJECT FOLLOW THE STEPS:-
1:- RUN THE app.py FILE IN THE PROJECT IT WILL START YOUR BACKEND SERVER
2:- YOUR KAFKA BROKER SHOULD RUN PARALLEL IN ANOTHER TERMINAL (CMD)
3:- RUN THE kafka_producer.py file
4:- RUN THE kafka_consumer.py file
5:- Now open web browser and type the url http://127.0.0.1:5000/
6:- THE Project will start and live anomaly detection dashboard will appear 

