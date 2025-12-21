#!/bin/bash
# Clone all non-archived, non-fork PaystackOSS repositories
cd /home/ubuntu/paystacog/integrations/PaystackOSS

repos=(
  "plugin-payment-forms-for-wordpress"
  "plugin-wpjobster"
  "plugin-paid-membership-pro"
  "plugin-sprout-invoices"
  "plugin-memberpress"
  "paystack-cli"
  "sample-gift-store"
  "sample-movie-ticket"
  "sample-backend"
  "sample-vue"
  "sample-kix"
  "pay-lender"
  "sample-react"
  "plugin-gravity-forms"
  "FoodCheckout"
  "sample-restaurant"
  "sample-logistics"
  "openapi"
  "paystack-node"
  "paystack-python"
  "tees-store"
  "tees-store-api"
  "sample-gift-store-api"
  "sample-android-webview"
  "sample-subscriptions-app"
  "Bubble-Plugin-Paystack"
  "sample-wallet-app"
  "plugin-the-events-calendar"
  "custom-forms-php"
  "sample-redirect"
  "doc-code-snippets"
  "sample-node"
  "sample-shoes-android"
  "sample-emoji"
  "sample-registration-flutter"
  "sample-registration-react-native"
  "apple-pay-react"
  "apple-pay-demo"
  "sample-express-backend"
  "paystack_flutter"
  "paystack-transaction-server"
  "sample-subscription-backend"
)

for repo in "${repos[@]}"; do
  echo "Cloning PaystackOSS/$repo..."
  if gh repo clone "PaystackOSS/$repo" "$repo" -- --depth 1 2>/dev/null; then
    rm -rf "$repo/.git"
    echo "✓ $repo cloned and .git removed"
  else
    echo "✗ Failed to clone $repo"
  fi
done

echo "PaystackOSS cloning complete!"
