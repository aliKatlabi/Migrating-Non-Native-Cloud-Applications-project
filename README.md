# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Service Category | Service Type | Region | Description | Estimated Monthly Cost |
| ---------------- | ------------ | ------ | ----------- | ---------------------- |
| Web              | Azure Communication Services | West Europe | Email: 100000 Email sent per month | $25.00 |
| Storage          | Storage Accounts | West Europe | Premium Block Blob Storage, Flat Namespace, ZRS Redundancy, Hot Access Tier, 1,000 GB Capacity - Pay as you go, 10 x 10,000 Write operations, 10 x 10,000 List and Create Container Operations, 10 x 10,000 Read operations, 1 x 10,000 Other operations. 1,000 GB Data Retrieval, 1,000 GB Data Write, SFTP disabled | $260.19 |
| Compute          | App Service | West Europe | Premium V2 Tier; 1 P3V2 (4 Core(s), 14 GB RAM, 250 GB Storage) x 730 Hours; Linux OS; 0 SNI SSL Connections; 0 IP SSL Connections; 0 Custom Domains; 0 Standard SLL Certificates; 0 Wildcard SSL Certificates | $337.26 |
| Compute          | Azure Functions | West Europe | Premium tier, Pay as you go, EP2: 2 Cores(s), 7 GB RAM, 250 GB Storage, 1 Pre-warmed instances, 1 Additional scaled out units | $617.14 |
| Databases        | Azure Database for PostgreSQL | West Europe | Flexible Server Deployment, General Purpose Tier, 1 D2ds v5 (2 vCores) x 730 Hours (Pay as you go), Storage - Premium SSD, 5 GiB Storage, 0 Provisioned IOPS, 0 GiB Additional Backup storage - LRS redundancy, without High Availability | $155.44 |
| Integration      | Service Bus | West Europe | Premium tier: 1 daily message units x 1 partition(s) x 730 Hours | $677.08 |
| Support          | Support | - | - | $0.00 |
| **Total**        | - | - | - | **$2,072.11** |


you can find the estimation link here : [Estimated monthly cost](https://azure.com/e/5166714d869e4be68ff3ff00c8c01210)

## Architecture Explanation

- **Azure App Service** handles the main web application, providing a reliable and scalable platform for hosting your web app.
- **Azure Functions** allows you to offload background processing tasks and handle event-driven scenarios without managing servers.
- **Azure Service Bus** ensures reliable and decoupled communication between different components of the application, improving scalability and resilience.
- **Azure Communication Services** adds rich communication features to your application, enhancing user interaction and engagement.

This combination of services leverages the strengths of each component, resulting in a well-architected solution that can handle a wide range of scenarios and workloads.