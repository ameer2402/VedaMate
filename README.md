Environment Setup (.env file)
This application requires access to Google Cloud services to function. You must provide your own API credentials in an environment file. This is a critical step.
Step 1: Create the .env File
In the root directory of the project (the same folder that contains app.py), create a new file and name it exactly .env.
Step 2: Add Content to the .env File
Copy the following template and paste it into your new .env file. You will then replace the placeholder values with your actual keys obtained in the next steps.
code
Env
# .env file

# Key for Google AI services (Gemini, Embeddings) and Google Search
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"

# Unique ID for your Programmable Search Engine
GOOGLE_CSE_ID="YOUR_GOOGLE_CSE_ID_HERE"
Step 3: Obtain Your Credentials
Follow these instructions carefully to get the required values.
Important Note on Google Accounts
It is highly recommended to use a personal Google Account (e.g., @gmail.com) to create a new Google Cloud project for this application. Corporate, school, or organizational accounts often have security policies that can block the APIs needed, causing 403 Forbidden errors.
A. How to Get Your GOOGLE_API_KEY
This single key will power both the Gemini AI models and the Custom Search API.
Create a Google Cloud Project:
Go to the Google Cloud Console.
It is best to use an Incognito/Private browser window to ensure you can log in with your personal Google account.
Create a New Project. Give it a name like "AI Teaching Assistant".
Enable the Required APIs:
You must enable two different APIs in your new project.
Generative Language API (for Gemini):
In your project, go to the search bar and type "Generative Language API".
Select it and click the blue "ENABLE" button.
Custom Search API (for Web Search):
Go to the search bar and type "Custom Search API".
Select it and click the blue "ENABLE" button.
Create the API Key:
In the navigation menu (☰), go to APIs & Services > Credentials.
Click + CREATE CREDENTIALS at the top and select API key.
A new key will be generated. Click the copy icon to copy it.
Paste this value into your .env file for GOOGLE_API_KEY.
B. How to Get Your GOOGLE_CSE_ID
This is the unique identifier for your custom search engine.
Go to the Programmable Search Engine Control Panel:
Navigate to https://programmablesearchengine.google.com/.
Create a New Search Engine:
Click the "Add" or "Create a new search engine" button.
Give your search engine a name (e.g., "My App Search").
Crucially: In the setup options, find and turn ON the setting for "Search the entire web". This is required for the application to find relevant information.
Copy the Search Engine ID:
After creating the engine, you will be taken to its control panel.
On the Basics > Setup tab, find the "Search engine ID" field.
Click the copy button to copy the ID.
Paste this value into your .env file for GOOGLE_CSE_ID.
Once you have replaced both placeholder values in your .env file and saved it, your application will have the necessary credentials to run successfully.
