
import json
import requests
import mlflow

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("RetailSphere_Agent_Evaluation")
mlflow.tracing.enable()

# ==========================================
# 1. Ollama configuration
# ==========================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:7b"


# ==========================================
# 2. Load Databricks Gold data
# ==========================================

with open("data/retailsphere_data.json", "r") as file:
    gold_data = json.load(file)

gold_sales = gold_data["gold_sales"]
product_performance = gold_data["gold_product_performance"]
state_sales = gold_data["gold_state_sales"]
monthly_revenue = gold_data["gold_monthly_revenue"]


# ==========================================
# 3. Analytics functions
# ==========================================
@mlflow.trace
def get_total_revenue():

    total = sum(
        float(row["item_revenue"])
        for row in gold_sales
    )

    return {
        "total_revenue": round(total, 2),
        "currency": "INR"
    }

@mlflow.trace
def get_top_products(limit=5):

    return sorted(
        product_performance,
        key=lambda row: float(row["total_revenue"]),
        reverse=True
    )[:limit]

@mlflow.trace
def get_state_revenue():

    return sorted(
        state_sales,
        key=lambda row: float(row["total_revenue"]),
        reverse=True
    )

@mlflow.trace
def get_monthly_revenue():

    return sorted(
        monthly_revenue,
        key=lambda row: row["sales_month"]
    )

@mlflow.trace
def get_top_products_revenue_contribution(limit=3):

    top_products = get_top_products(limit)

    top_product_revenue = sum(
        float(product["total_revenue"])
        for product in top_products
    )

    total_business_revenue = get_total_revenue()["total_revenue"]

    percentage = (
        top_product_revenue / total_business_revenue * 100
        if total_business_revenue > 0
        else 0
    )

    return {
        "products": [
            product["product_name"]
            for product in top_products
        ],
        "top_products_revenue": round(top_product_revenue, 2),
        "total_business_revenue": round(total_business_revenue, 2),
        "revenue_contribution_percentage": round(percentage, 2)
    }


# ==========================================
# 4. Tool registry
# ==========================================

tool_functions = {
    "get_total_revenue": get_total_revenue,
    "get_top_products": get_top_products,
    "get_state_revenue": get_state_revenue,
    "get_monthly_revenue": get_monthly_revenue,
    "get_top_products_revenue_contribution":
        get_top_products_revenue_contribution
}


# ==========================================
# 5. Tool validation and execution
# ==========================================

def execute_tool(function_name, arguments):

    if function_name not in tool_functions:
        raise ValueError(f"Tool not allowed: {function_name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary.")

    if function_name in (
        "get_top_products",
        "get_top_products_revenue_contribution"
    ):

        default_limit = (
            5 if function_name == "get_top_products" else 3
        )

        limit = arguments.get("limit", default_limit)

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("Product limit must be an integer.")

        if not 1 <= limit <= 5:
            raise ValueError("Product limit must be between 1 and 5.")

        if set(arguments) != {"limit"}:
            raise ValueError("Unsupported tool arguments.")

        return tool_functions[function_name](limit)

    if arguments:
        raise ValueError(
            f"This tool does not accept arguments: {function_name}"
        )

    return tool_functions[function_name]()


# ==========================================
# 6. Tool schemas for Qwen
# ==========================================

tools = [

    {
        "type": "function",
        "function": {
            "name": "get_total_revenue",
            "description": "Get total delivered sales revenue in INR.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_top_products",
            "description": "Get products ranked by total sales revenue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top products to return, between 1 and 5.",
                        "default": 5
                    }
                }
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_state_revenue",
            "description": "Get sales revenue grouped by Indian state.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_monthly_revenue",
            "description": "Get monthly sales revenue trends.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_top_products_revenue_contribution",
            "description": (
                "Calculate the exact revenue contribution percentage "
                "of the top products using Python."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top products to include, between 1 and 5.",
                        "default": 3
                    }
                }
            }
        }
    }

]


# ==========================================
# 7. Conversation memory and tool tracking
# ==========================================

conversation_history = []

last_tool_calls = []


# ==========================================
# 8. Agent execution
# ==========================================
@mlflow.trace
def run_agent(question):

    global conversation_history
    global last_tool_calls

    # Reset tool tracking for this question
    last_tool_calls = []

    messages = [
        {
            "role": "system",
            "content": (
                "You are RetailSphere, an Indian retail analytics assistant. "
                "Use available tools to answer questions about sales. "
                "Always use Indian Rupees (₹). "
                "Never invent analytics results. "
                "Use the revenue contribution tool for percentage calculations. "
                "Use Python tool results for financial calculations. "
                "Do not confuse revenue with profit. "
                "Explain business insights clearly."
            )
        }
    ]

    messages.extend(conversation_history)

    messages.append({
        "role": "user",
        "content": question
    })

    # First request: ask Qwen to select tools
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "tools": tools,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    message = response.json()["message"]

    tool_calls = message.get("tool_calls", [])

    # Record selected tools for evaluation
    last_tool_calls = [
        call["function"]["name"]
        for call in tool_calls
    ]

    # No tool selected
    if not tool_calls:

        answer = message.get(
            "content",
            "No response generated."
        )

        conversation_history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ])

        conversation_history = conversation_history[-10:]

        return answer

    # Add assistant tool-call message
    messages.append(message)

    # Execute selected tools
    for call in tool_calls:

        function_name = call["function"]["name"]

        arguments = call["function"].get("arguments", {})

        result = execute_tool(function_name, arguments)

        print("\nTool executed:", function_name)
        print("Tool result:", result)

        messages.append({
            "role": "tool",
            "tool_name": function_name,
            "content": json.dumps(result, default=str)
        })

    # Second request: ask Qwen to explain results
    final_response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False
        },
        timeout=120
    )

    final_response.raise_for_status()

    final_answer = final_response.json()["message"]["content"]

    # Save conversation history
    conversation_history.extend(messages[1:])

    conversation_history.append({
        "role": "assistant",
        "content": final_answer
    })

    conversation_history = conversation_history[-10:]

    return final_answer


# ==========================================
# 9. Basic validation tests
# ==========================================

def run_validation_tests():

    print("\n========== RETAILSPHERE VALIDATION ==========")

    print("\nTEST 1: Valid product request")

    result = execute_tool(
        "get_top_products",
        {"limit": 3}
    )

    print("Returned products:", len(result))
    print("Validation successful:", result)

    print("\nTEST 2: Invalid product limit")

    try:
        execute_tool(
            "get_top_products",
            {"limit": 100}
        )

    except ValueError as error:
        print("Validation successful:", error)

    print("\nTEST 3: Unauthorized tool")

    try:
        execute_tool(
            "delete_customer_data",
            {}
        )

    except ValueError as error:
        print("Validation successful:", error)

    print("\nTEST 4: Revenue contribution")

    result = execute_tool(
        "get_top_products_revenue_contribution",
        {"limit": 3}
    )

    print("Validation successful:", result)

    print("\n========== TESTS COMPLETED ==========")


# ==========================================
# 10. Interactive application
# ==========================================

if __name__ == "__main__":

    run_validation_tests()

    print("\n===================================")
    print("       RETAILSPHERE AI AGENT")
    print("===================================")

    while True:

        question = input(
            "\nAsk RetailSphere (type exit to quit): "
        )

        if question.lower().strip() == "exit":

            print("RetailSphere session ended.")
            break

        try:

            answer = run_agent(question)

            print("\nRetailSphere:", answer)

        except requests.RequestException as error:

            print("\nOllama connection error:", error)

        except (ValueError, KeyError, TypeError) as error:

            print("\nTool execution error:", error)

        except Exception as error:

            print("\nUnexpected error:", error)
