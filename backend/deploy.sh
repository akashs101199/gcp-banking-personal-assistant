set -e

source .env

echo "🚢 Deploying Nova Banking AI"
echo "============================"

echo "📦 Building main application..."
gcloud builds submit --config cloudbuild.yaml

echo "📦 Building MCP server..."
gcloud builds submit --config cloudbuild-mcp.yaml

echo "✅ Deployment complete!"
echo ""
echo "📝 Service URLs:"
gcloud run services describe nova-banking-ai --region=$GCP_REGION --format='value(status.url)'
gcloud run services describe nova-mcp-server --region=$GCP_REGION --format='value(status.url)'
echo ""