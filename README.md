# Jira to Azure Resource Manager (ARM) Deployment Pipeline

This project automates the deployment of Azure resources (like VMs, web apps, etc.) based on information received from Jira intake forms. It utilizes Jira webhooks, Azure Functions, and Azure DevOps pipelines to achieve this.

## Overview

The workflow consists of the following steps:

1.  **Jira Intake Form Submission:** Users submit intake forms in Jira, providing details about the resources they need to deploy.
2.  **Jira Webhook Trigger:** Upon form submission, a Jira webhook is triggered, sending the form data to an Azure Function.
3.  **Azure Function Processing:**
    * The Azure Function receives the webhook data.
    * It parses the JSON payload to extract relevant information (resource type, name, configuration).
    * It validates the extracted data.
    * It triggers an Azure DevOps pipeline, passing the extracted data as pipeline parameters.
4.  **Azure DevOps Pipeline Execution:**
    * The Azure DevOps pipeline receives the data parameters.
    * It uses the Azure Resource Manager (ARM) APIs to interact with Azure and deploy the specified resources (VMs, web apps, etc.).
    * It uses a service connection to authenticate with Azure.
    * It reports the success or failure of the deployment.
5.  **Deployment Result:**
    * The pipeline's execution result is logged and can optionally be communicated back to Jira.

## Architecture Diagram


