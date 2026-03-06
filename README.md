The AI-Driven Healthcare Anomaly Detection System is an end-to-end real-time monitoring and decision-support platform designed to detect abnormal patterns in patient vital signs and generate early health risk alerts. Unlike traditional healthcare monitoring systems that rely on static thresholds or post-incident analysis, this system continuously analyzes live physiological data streams using machine learning models to identify anomalies as they occur.

The system ingests real-time patient vitals such as heart rate, oxygen saturation (SpO₂), body temperature, and blood pressure through a streaming pipeline powered by Apache Kafka. These vitals are processed by advanced anomaly detection models, including an Autoencoder Neural Network and Isolation Forest, which compute anomaly scores and classify patient conditions into severity levels such as LOW, MEDIUM, and HIGH.

Detected anomalies are stored in a PostgreSQL database, visualized on an interactive Flask-based dashboard, and critical alerts automatically trigger email notifications to healthcare administrators. The project demonstrates the practical application of machine learning, real-time data streaming, backend APIs, and dashboard visualization in solving real-world healthcare monitoring challenges.



