# Apache Kafka: The "High-Speed Conveyor Belt" for Data

Imagine you have a **Post Office** (The Broker).
Messages come in faster than any single mailman can deliver them. You need a system to handle millions of letters per second without losing any. That system is **Kafka**.

## 1. The Core Concept: The "Log"
At its heart, Kafka is just a **Commit Log**. Think of it like a text file where you can only **append** new lines at the bottom. You cannot delete or change old lines.
- **Old Data**: Stays there for a set time (e.g., 7 days).
- **New Data**: Gets added to the end.

## 2. Key Terminology

### 🗣️ Topic (The "Channel")
A **Topic** is like a category or a folder.
*   **Analogy**: A specific slack channel (e.g., `#general`, `#alerts`).
*   **In Our Project**: passing `raw_news_topic` contains all the raw scraped JSONs.

### 🏭 Producer (The "Writer")
The app that **sends** data.
*   **Analogy**: The person typing a message.
*   **In Our Project**: Our **Scrapers** (BBC, CNN) are producers. They "shout" news into the Topic.

### 🛒 Consumer (The "Reader")
The app that **reads** data.
*   **Analogy**: The person reading the message.
*   **In Our Project**: **Spark** is the consumer. It listens to the Topic and processes messages as they arrive.
*   *Note*: Consumers can read at their own speed. If Spark crashes, Kafka keeps the messages safe until Spark comes back.

### 📦 Broker (The "Server")
The physical server (or container) running Kafka. Ideally, you have a cluster of these for safety.

## 3. How It Scales: Partitions 🍰
If a Topic gets too big for one server, Kafka splits it into **Partitions**.
*   **Partition 0**: Holds messages A, C, E...
*   **Partition 1**: Holds messages B, D, F...
This allows multiple consumers to read from the same topic simultaneously (Parallel Processing).

## 4. Keeping Track: Offsets 🔖
How does Spark know which message to read next?
*   **Offset**: A simple ID number (0, 1, 2, 3...).
*   It works like a **bookmark**.
*   Spark says: *"I have finished reading message #50. Next time, give me #51."*

## 5. What is Zookeeper? 🦁
Kafka is a distributed system (many moving parts). **Zookeeper** is the manager.
*   It keeps track of which Brokers are alive.
*   It manages configuration.
*   *Modern Kafka (KRaft mode) is removing Zookeeper, but most production systems still use it.*

---

## Summarized Flow in Our Project

1.  **BBC Scraper** (Producer) finds an article.
2.  It sends `{ "title": "News..." }` to **Kafka Topic** `raw_news`.
3.  **Kafka** saves it to disk (Partition 0, Offset 105).
4.  **Spark** (Consumer) asks: "Give me new data after Offset 104."
5.  **Kafka** sends the article.
6.  **Spark** cleans it and saves the specific offset (105) as "Done".

This "decouples" the system. The Scraper doesn't care if Spark is slow or offline. It just dumps data into Kafka and moves on.
