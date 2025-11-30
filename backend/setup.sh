#!/bin/bash

set -e

echo "🚀 Nova Banking AI - Automated Setup"
echo "===================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed"
    exit 1
fi

# Prompt for project ID
read -p "Enter your GCP Project ID: " PROJECT_ID
read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

echo "📋 Project ID: $PROJECT_ID"
echo "📍 Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

echo "✅ Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  speech.googleapis.com \
  texttospeech.googleapis.com \
  cloudtrace.googleapis.com \
  monitoring.googleapis.com \
  cloudbuild.googleapis.com

echo "✅ Creating service account..."
gcloud iam service-accounts create nova-backend-sa \
  --display-name="Nova Banking AI Service Account" \
  --quiet || echo "Service account already exists"

echo "✅ Granting IAM permissions..."
for role in "roles/bigquery.admin" "roles/storage.admin" "roles/aiplatform.user" "roles/cloudtrace.agent"; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:nova-backend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="$role" \
    --quiet
done

echo "✅ Creating Cloud Storage buckets..."
gsutil mb -l $REGION gs://$PROJECT_ID-banking-ai 2>/dev/null || echo "Bucket already exists"
gsutil mb -l $REGION gs://$PROJECT_ID-banking-analytics 2>/dev/null || echo "Bucket already exists"

echo "✅ Creating BigQuery dataset..."
bq mk --location=$REGION --dataset $PROJECT_ID:nova_banking_data 2>/dev/null || echo "Dataset already exists"

echo "✅ Seeding BigQuery data..."
python3 bq_seed_data.py

echo "✅ Generating API key..."
API_KEY=$(openssl rand -hex 32)
echo "API_KEY=$API_KEY" > .env
echo "GCP_PROJECT_ID=$PROJECT_ID" >> .env
echo "GCP_REGION=$REGION" >> .env
echo "GCS_BUCKET_NAME=$PROJECT_ID-banking-ai" >> .env

echo ""
echo "🎉 Setup Complete!"
echo "===================="
echo "Your API Key: $API_KEY"
echo "Save this key securely!"
echo ""
echo "Next steps:"
echo "1. Review .env file"
echo "2. Run: ./deploy.sh to deploy services"
echo ""
