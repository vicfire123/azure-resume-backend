import os
import azure.functions as func
import logging
import json
from azure.cosmos import CosmosClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Replace these values with your actual Cosmos DB details from the portal
COSMOS_DB_CONNECTION_STRING = os.environ.get("COSMOS_DB_CONNECTION_STRING")
DATABASE_NAME = "AzureResume"
CONTAINER_NAME = "Counter"

@app.route(route="GetResumeCounter")
def GetResumeCounter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Initialize the Cosmos Client using your connection string
        client = CosmosClient.from_connection_string(COSMOS_DB_CONNECTION_STRING)
        database = client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)

        # 1. Read the current counter item (id="1", partition key="1")
        counter_item = container.read_item(item="1", partition_key="1")

        # 2. Increment the count value by 1
        counter_item['count'] += 1

        # 3. Update the item back inside the database container
        container.upsert_item(counter_item)

        # 4. Construct a clean JSON response to send back to the web browser
        response_data = {
            "count": counter_item['count']
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*", # Allows your website domain to securely pull this API
                "Access-Control-Allow-Methods": "GET"
            }
        )

    except Exception as e:
        logging.error(f"Error handling database transaction: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to update counter"}),
            status_code=500,
            mimetype="application/json"
        )