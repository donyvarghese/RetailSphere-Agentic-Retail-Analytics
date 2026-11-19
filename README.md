# RetailSphere – Agentic AI-Powered Retail Analytics Platform

An end-to-end retail analytics project combining Databricks, Apache Spark, Python, local Large Language Models (LLMs), MLflow, and Streamlit.

RetailSphere transforms raw retail transaction data into business insights through a Medallion data architecture and an AI-powered analytics assistant.

## Project Overview

RetailSphere demonstrates how modern data engineering and Agentic AI techniques can be combined to build an interactive retail analytics platform.

The project processes synthetic retail data through Bronze, Silver, and Gold layers in Databricks. The resulting Gold analytics are exported as a JSON snapshot and used by a locally running AI agent.

Users can explore business performance through a Streamlit dashboard or ask natural-language questions using the AI retail assistant.

## Architecture

```text
        Synthetic Retail Data
                  |
                  v
          Databricks Free Edition
                  |
                  v
          Bronze Data Layer
          Raw retail datasets
                  |
                  v
          Silver Data Layer
          Cleaned and transformed
                  |
                  v
           Gold Data Layer
          Business-ready analytics
                  |
                  v
          Export Gold JSON
                  |
                  v
          Local Python Agent
                  |
          +-------+-------+
          |               |
          v               v
      Ollama          Python Analytics
      Qwen 2.5 7B         Tools
          |               |
          +-------+-------+
                  |
                  v
             AI Responses
                  |
                  v
           Streamlit Dashboard

          MLflow: Tracing and Evaluation
```

**Important:** The AI agent runs locally on the developer's machine. It uses an exported snapshot of Databricks Gold data rather than a live Databricks connection. The snapshot must be re-exported when the underlying Gold data changes.

## Technology Stack

| Area | Technology |
|---|---|
| Data engineering | Databricks Free Edition |
| Data processing | Apache Spark / PySpark |
| Data storage | Delta tables |
| Architecture | Medallion (Bronze, Silver, Gold) |
| Programming | Python |
| Local LLM | Qwen 2.5 7B |
| LLM runtime | Ollama |
| Agent observability | MLflow |
| Dashboard | Streamlit |
| Data exchange | JSON |

## Data Engineering Pipeline

### Bronze Layer
- Ingest synthetic retail customers, products, orders, and order items.
- Store raw datasets as Delta tables.

### Silver Layer
- Handle duplicate records.
- Clean and standardise customer data.
- Convert data types.
- Validate order and product records.

### Gold Layer
- Join customer, product, order, and order-item datasets.
- Calculate item-level revenue.
- Exclude cancelled orders.
- Generate business-level analytical tables.

### Gold Tables

- `gold_sales`
- `gold_monthly_revenue`
- `gold_product_performance`
- `gold_state_sales`

## AI Retail Assistant

The local AI assistant uses Qwen 2.5 7B through Ollama.

It can interpret natural-language questions and select from registered Python analytics tools.

Examples:
- What is the total business revenue?
- Show the top three products by revenue.
- Which Indian state generated the highest revenue?
- Show monthly revenue.
- What percentage of revenue came from the top three products?

The agent uses tool validation to restrict execution to registered analytics functions.

## MLflow Observability and Evaluation

MLflow is used for:
- Agent execution tracing.
- Nested function/tool tracing.
- Experiment tracking.
- Evaluation metrics.
- Recording agent tool-selection behaviour.

The current evaluation suite contains seven tests covering deterministic analytics, tool validation, and LLM tool selection.

The reported test result is 7/7 passed on the synthetic project dataset. This is a development evaluation result, not a production reliability guarantee.

## Streamlit Dashboard

The dashboard provides:
- Business overview and revenue KPIs.
- Monthly revenue analysis.
- Product performance.
- Regional revenue analysis.
- AI-powered natural-language analytics.

## Project Results

The current synthetic dataset produces the following results:

| Metric | Result |
|---|---:|
| Total revenue | ₹184,000 |
| Gold sales records | 9 |
| Products | 5 |
| Monthly reporting periods | 3 |
| States represented | 5 |

### Top Products by Revenue

| Product | Revenue |
|---|---:|
| Laptop | ₹110,000 |
| Mobile | ₹50,000 |
| Headphones | ₹10,000 |

These figures are based on the project's synthetic dataset and are intended to demonstrate the analytics pipeline.


## Project Limitations

- The retail dataset is synthetic.
- The AI agent uses a static exported Gold JSON snapshot.
- Refreshing the analytics requires exporting the latest Gold data again.
- The local LLM requires Ollama and sufficient local computing resources.
- Revenue analysis does not represent profit, since product costs and operating expenses are not modelled.
- The project is a portfolio demonstration and is not a production retail deployment.

## Future Enhancements

- Live data connectivity between the agent and Databricks.
- Additional inventory and profitability analytics.
- More comprehensive agent evaluation.
- Improved tool governance and SQL safety.
- Production deployment and monitoring.

## Author

Developed as a hands-on portfolio project demonstrating data engineering, retail analytics, local LLM integration, Agentic AI, and application development.

## License

MIT License