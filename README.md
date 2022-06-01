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

 | Azure Resource | Service Tier | Monthly Cost |
 | ------------ | ------------ | ------------ |
 | *Azure Postgres Database* |Basic     |25.32              |
 | *Azure Service Bus*   |Basic         |0.05              |
 | *Storage Account*   |General V1      |0.00              |
 | *Application Service*   |App Svc Plan F1 |0.00              |
 | *Function App*   |Region East US Tier Consumption        |0.00             |


 |  |  |      |              |

 ## Architecture Explanation
 This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

The Architecture selection for the Web Application migration was Azure Web App for the following reasons:

1. As current web application is not scalable to handle user load at peak we need the high availability and auto-scaling offered by Azure Application Service and also the rest of the benefits like :
 	a) Vertical and Horizontal Scaling
2. As the current web application is developed in python that is one of the limited set of programming languages include in the Azure Application Service.
3. Also the Application Service have support for Linux.
4. The cost is based on the Application Service Plan so we can play with our budget and select the best option according to it.

Also with this migration option the infrastructure is manage for us, so now we can focus on business logic and this option is quick and easy to set up, typically cheaper with some free options.

For the Azure Function :
 As when the admin sends out notifications it's currently taking a long time because it's looping through all attendees resulting in some HTTP timeout exceptions so we need to move the logic to a background job that can execute the process asynchronously.
The selection of the Azure Service Bus Queue was based on :
Queues offer First In, First Out (FIFO) message delivery to one or more competing consumers. That is, receivers typically receive and process messages in the order in which they were added to the queue. 
And, only one message consumer receives and processes each message. A key benefit of using queues is to achieve temporal decoupling of application components. 
In other words, the producers (senders) and consumers (receivers) don't have to send and receive messages at the same time. 
That's because messages are stored durably in the queue. Furthermore, the producer doesn't have to wait for a reply from the consumer to continue to process and send messages.
A related benefit is load-leveling, which enables producers and consumers to send and receive messages at different rates. In many applications, the system load varies over time. 
However, the processing time required for each unit of work is typically constant. 
Intermediating message producers and consumers with a queue means that the consuming application only has to be able to handle average load instead of peak load. The depth of the queue grows and contracts as the incoming load varies. 
This capability directly saves money regarding the amount of infrastructure required to service the application load. 
As the load increases, more worker processes can be added to read from the queue. Each message is processed by only one of the worker processes. 
Furthermore, this pull-based load balancing allows for best use of the worker computers even if the worker computers with processing power pull messages at their own maximum rate. This pattern is often termed the competing consumer pattern.
Using queues to intermediate between message producers and consumers provides an inherent loose coupling between the components. Because producers and consumers aren't aware of each other, a consumer can be upgraded without having any effect on the producer.


