#!/bin/bash
# Generate a secure secret key for production deployment

echo "====================================="
echo "🔐 Secret Key Generator"
echo "====================================="
echo ""
echo "Generated SECRET_KEY for Railway:"
echo ""
openssl rand -hex 32
echo ""
echo "Copy this value and set it as SECRET_KEY in Railway environment variables."
echo ""
