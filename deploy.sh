#!/bin/bash

# PSM Deployment Helper Script

# 1. Clean up previous deployment artifacts to prevent "Nonce too low" errors
echo "Cleaning up previous deployment artifacts..."
rm -rf broadcast/ cache/
forge clean

# 2. Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found!"
    exit 1
fi

# 3. Check for required variables
if [ -z "$PRIVATE_KEY" ]; then
    echo "Error: PRIVATE_KEY not set in .env"
    exit 1
fi

if [ -z "$RPC_URL" ]; then
    echo "Error: RPC_URL not set in .env"
    exit 1
fi

# 4. Run deployment
echo "Starting deployment..."
echo "Using RPC: $RPC_URL"
echo "Gas Price: 30 gwei"

# Use 'yes' to bypass the "Script contains a transaction..." warning
# Use --no-cache to force fresh nonce lookup
yes | forge script script/KssLitePsmDeploy.s.sol \
    --rpc-url "$RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --broadcast \
    --legacy \
    --gas-limit 10000000 \
    --gas-price 30000000000 \
    --no-cache \
    -vvv

echo "Deployment finished."
