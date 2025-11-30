# Google Cloud Platform (GCP) Setup Guide

This guide will walk you through setting up your Google Cloud environment from scratch. You need this to get the `service-account-key.json` and `PROJECT_ID` required for the application.

## Step 1: Create a Google Cloud Project

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Sign in with your Google Account.
3.  In the top navigation bar, click the **Project Dropdown** (it might say "Select a project" or show a current project name).
4.  Click **New Project** (top right of the popup).
5.  **Project Name**: Enter a name (e.g., `nova-banking-ai`).
6.  **Location**: You can leave it as "No organization" if you are using a personal account.
7.  Click **Create**.
8.  Wait a moment, then click **Select Project** in the notification, or use the dropdown at the top to select your new project.

## Step 2: Enable Required APIs

The application uses three specific Google Cloud services. You must enable them for your project.

1.  Open the **Navigation Menu** (three lines in top left) -> **APIs & Services** -> **Library**.
2.  Search for and enable the following three APIs (repeat for each):
    *   **Vertex AI API**
    *   **Cloud Speech-to-Text API**
    *   **Cloud Text-to-Speech API**
    *   **BigQuery API**
3.  To enable an API, click on it in the search results and click the blue **Enable** button.
4.  **CRITICAL STEP**: After enabling Vertex AI, go to **Vertex AI** -> **Model Garden**.
    *   Search for **Gemini 1.5 Flash**.
    *   Click **View Details**.
    *   Click **Enable** (if available) or ensure you have access.
    *   Do the same for **Gemini 1.5 Pro**.

## Step 3: Create a Service Account

A Service Account allows the backend code to authenticate with Google Cloud securely.

1.  Go to **Navigation Menu** -> **IAM & Admin** -> **Service Accounts**.
2.  Click **+ CREATE SERVICE ACCOUNT** (top center).
3.  **Service account details**:
    *   **Name**: `nova-backend-sa` (or similar).
    *   Click **Create and Continue**.
4.  **Grant this service account access to project**:
    *   Click the **Select a role** dropdown.
    *   Select **Basic** -> **Owner** (For simplicity in this demo. *Note: In a real production app, you would grant specific roles like "Vertex AI User", "Cloud Speech Client", etc.*).
    *   Click **Continue**.
5.  Click **Done**.

## Step 4: Download the JSON Key

1.  You should now see your new service account in the list.
2.  Click on the **Email address** of the service account (or click the three dots under "Actions" -> Manage details).
3.  Go to the **KEYS** tab (top bar).
4.  Click **ADD KEY** -> **Create new key**.
5.  Select **JSON**.
6.  Click **Create**.
7.  A file will automatically download to your computer. **This is your credential file.**

## Step 5: Configure the Application

1.  **Rename** the downloaded file to `service-account-key.json`.
2.  **Move** this file into the `backend/` folder of your project.
    *   Path: `.../gcp-banking-customer-service/backend/service-account-key.json`
3.  Find your **Project ID**:
    *   It is visible in the Project Dropdown at the top of the Google Cloud Console.
    *   It is also inside the JSON key file you just downloaded (look for `"project_id": "..."`).
4.  Open the `backend/.env` file in your code editor.
5.  Update the values:

```env
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
PROJECT_ID=your-project-id-here  <-- Paste your Project ID
LOCATION=us-central1             <-- You can keep this default
API_KEY=secret-demo-key-12345    <-- Keep this as is (it's for the app security)
```

## Summary Checklist

- [ ] Project Created
- [ ] Vertex AI API Enabled
- [ ] Speech-to-Text API Enabled
- [ ] Text-to-Speech API Enabled
- [ ] BigQuery API Enabled
- [ ] Service Account Created (with Owner role)
- [ ] JSON Key downloaded and renamed to `service-account-key.json`
- [ ] Key placed in `backend/` folder
- [ ] `backend/.env` updated with `PROJECT_ID`

You are now ready to run `docker-compose up --build`!
