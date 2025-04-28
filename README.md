# Food-Image-Recognition

A **Kafka-based Food Image Recognition Service**.  
It consumes image metadata messages from Kafka, downloads images from **MinIO**, predicts food classes using a pre-trained **Keras model**, and sends the prediction results back to Kafka.

---

## 🚀 Setup Instructions

> Make sure you have [Poetry](https://python-poetry.org/docs/#installation) installed.

```bash
# 1. Update your PATH (if Poetry is installed locally)
export PATH="/root/.local/bin:$PATH"
source ~/.bashrc

# 2. Copy the environment configuration
cp .env.sample .env

# 3. Install project dependencies
poetry install

# 4. Run the service
poetry run python3 main.py
```

---

## 🧪 Testing

To manually produce a test message to Kafka:

```bash
poetry run python3 kafka-producer.py
```

---

## ⚙️ System Requirements

### Kafka Setup

```text
- Ensure a Kafka broker is running and accessible.
- You can quickly set up a local broker using Docker images such as:
  - confluentinc/cp-kafka
  - bitnami/kafka
- Required Kafka topics must be pre-created, or configure the broker to auto-create topics automatically.
```

### MinIO Setup

```text
- Ensure your MinIO server is running and accessible.
- Create the required bucket manually if necessary.
- MinIO credentials (access key, secret key, endpoint, bucket name) must match the .env configuration.
- Optionally, use the MinIO Console (browser UI) for easier management.
```

### Model and Food Labels

```text
- The project expects a Keras model file named best_model_101class.keras at the project root directory.
- A food_names.csv file must be present containing sorted food labels, one label per line.
```

### Async Processing

```text
- The service uses a single asyncio event loop for non-blocking operations.
- Kafka producer operations are dispatched asynchronously using asyncio.to_thread to avoid blocking.
```

---

# ✨ Happy Coding and Delicious Predictions!