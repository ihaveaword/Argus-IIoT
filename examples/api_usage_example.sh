#!/bin/bash
# Example script to use the Architecture Audit API

BASE_URL="http://localhost:8000"

echo "================================================================================"
echo "Architecture Audit API - Usage Examples"
echo "================================================================================"
echo ""

# Check if server is running
echo "1. Checking API health..."
curl -s "${BASE_URL}/api/audit/health" | python3 -m json.tool
echo ""
echo ""

# Scan a repository
echo "2. Scanning repository..."
SCAN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/audit/scan" \
  -H "Content-Type: application/json" \
  -d "{\"directory_path\": \"$(pwd)/backend\"}")

echo "$SCAN_RESPONSE" | python3 -m json.tool

# Extract audit_id
AUDIT_ID=$(echo "$SCAN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('audit_id', ''))")

if [ -z "$AUDIT_ID" ]; then
  echo "Failed to get audit ID"
  exit 1
fi

echo ""
echo ""

# Get audit results
echo "3. Getting audit results for ID: $AUDIT_ID"
curl -s "${BASE_URL}/api/audit/audit/${AUDIT_ID}" | python3 -m json.tool | head -50
echo "..."
echo ""
echo ""

# List all audits
echo "4. Listing all audits..."
curl -s "${BASE_URL}/api/audit/audits" | python3 -m json.tool
echo ""
echo ""

# Generate report URL
REPORT_URL="${BASE_URL}/api/audit/report/${AUDIT_ID}"
echo "================================================================================"
echo "✅ Examples completed!"
echo "================================================================================"
echo ""
echo "View the interactive HTML report at:"
echo "  ${REPORT_URL}"
echo ""
echo "You can open this URL in your browser to see:"
echo "  • Architecture patterns visualization"
echo "  • API contracts analysis"
echo "  • Technology stack comparison"
echo "  • Downloadable ADR template"
echo ""
