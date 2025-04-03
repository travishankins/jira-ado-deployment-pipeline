import logging
import json
import requests
import os

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get the Jira webhook data
        req_body = req.get_json()
        logging.info(f"Jira Webhook Data: {req_body}")

        # Extract relevant information from Jira payload
        resource_type = req_body.get('resource_type')
        resource_name = req_body.get('resource_name')
        resource_config = req_body.get('resource_config')

        # Validate required fields
        if not resource_type or not resource_name or not resource_config:
            return func.HttpResponse(
                "Missing required fields (resource_type, resource_name, resource_config).",
                status_code=400
            )

        # Validate resource_config and serialize to json string.
        try:
            resource_config_json = json.dumps(resource_config)
        except (TypeError, ValueError) as e:
            logging.error(f"Error serializing resource_config: {e}")
            return func.HttpResponse(
                "Invalid resource_config format.",
                status_code=400
            )

        # Define Azure DevOps parameters from environment variables.
        ado_org = os.environ.get("ADO_ORG")
        ado_project = os.environ.get("ADO_PROJECT")
        ado_pipeline_id = os.environ.get("ADO_PIPELINE_ID")

        if not ado_org or not ado_project or not ado_pipeline_id:
            return func.HttpResponse(
                "Azure DevOps environment variables not set.",
                status_code=500
            )

        # Trigger Azure DevOps Pipeline with passed parameters
        trigger_ado_pipeline(ado_org, ado_project, ado_pipeline_id, resource_type, resource_name, resource_config_json)

        return func.HttpResponse(
            "Jira Webhook processed and Azure DevOps pipeline triggered.",
            status_code=200
        )

    except (KeyError, ValueError) as e:
        logging.error(f"Error parsing Jira Webhook: {e}")
        return func.HttpResponse(
            "Error parsing Jira Webhook data.",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return func.HttpResponse(
            "An unexpected error occurred.",
            status_code=500
        )

def trigger_ado_pipeline(ado_org, ado_project, ado_pipeline_id, resource_type, resource_name, resource_config):
    # The URL to trigger the Azure DevOps pipeline
    url = f"https://dev.azure.com/{ado_org}/{ado_project}/_apis/pipelines/{ado_pipeline_id}/runs?api-version=6.0"

    # Prepare the pipeline parameters
    parameters = {
        "resource_type": resource_type,
        "resource_name": resource_name,
        "resource_config": resource_config  # Pass the configuration as a string
    }

    # The payload for the API call to trigger the pipeline
    payload = {
        "templateParameters": parameters
    }

    try:
        # Send the POST request to trigger the pipeline without a PAT (Azure DevOps will use the Service Connection credentials)
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        logging.info(f"ADO Pipeline triggered. Status Code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error triggering ADO pipeline: {e}, Response: {response.text if 'response' in locals() else 'No response'}")
        raise #Re-raise the exception, so the azure function returns a 500 error.
    logging.info(f"ADO Pipeline triggered. Status Code: {response.status_code}")