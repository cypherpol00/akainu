# Akainu AI Dashboard

An enterprise-level asynchronous monitoring and log analysis platform designed to track, ingest, and process digital system metrics in real time. 

Akainu AI acts as a centralized dashboard that visualizes traffic anomalies, cybersecurity insights, and system performance logs driven by background workers and real-time WebSocket streams.

---

## 🏛️ Architecture Overview

The system is built using a modern, scalable backend stack designed to separate synchronous web requests from intensive background tasks and continuous event streaming.

* **Core Framework:** Django 5.x / Python 3.14
* **Asynchronous Engine:** Django Channels & Daphne (ASGI Server) for live WebSocket telemetry.
* **Task Orchestration:** Celery for distributed, non-blocking log analysis and AI evaluations.
* **Message Broker & Cache:** Redis acting as the high-performance transport layer.
* **Production Ingestion Gateway:** Nginx configured as a reverse proxy splitting traffic between HTTP (Gunicorn) and WebSockets (Daphne).

---

## 🚀 Production Deployment (Docker & AWS EC2)

This project is optimized to run inside isolated Docker containers on a Linux environment (such as Debian/Ubuntu on AWS EC2 Free Tier). This approach ensures native support for modern Redis protocol structures (`protocol=2` / `HELLO` command standards).

### Prerequisites
* Docker & Docker Compose
* Git

### Quick Start in Production

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/cypherpol00/akainu.git](https://github.com/cypherpol00/akainu.git)
   cd akainu
