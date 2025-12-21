#!/bin/bash
# Clone all non-archived, non-fork PaystackHQ repositories
cd /home/ubuntu/paystacog/integrations/PaystackHQ

repos=(
  "paystack-android"
  "paystack-ios"
  "plugin-magento"
  "plugin-icejoomla"
  "plugin-whmcs"
  "plugin-magento-2"
  "plugin-prestashop-1.6"
  "plugin-abantecart"
  "plugin-joomla-virtuemart-3"
  "plugin-cs-cart"
  "website-v1"
  "plugin-boxbilling"
  "library-android-pinpad"
  "plugin-engine-themes-directory-engine-freelance-engine"
  "plugin-prestashop-1.7"
  "plugin-wordpress-premiumpress"
  "plugin-os-class"
  "plugin-spc"
  "plugin-joomla-breezing-commerce-paystack-gateway"
  "plugin-enginethemes-freelanceengine1.7-1.8"
  "plugin-opencart-3.x"
  "documentation"
  "plugin-learnpress"
  "reimbursement-app"
  "nigerialogos"
  "plugin-paystack-resellerclub"
  "omnipay-paystack"
  "paystack-music-api"
  "checkout-ios"
  "checkout-android"
  "moodle-enrol_paystack"
  "publish-mavencentral"
  "paystack-sdk-ios"
  "plugin-odoo"
  "Marketplace-iOS"
)

for repo in "${repos[@]}"; do
  echo "Cloning PaystackHQ/$repo..."
  if gh repo clone "PaystackHQ/$repo" "$repo" -- --depth 1 2>/dev/null; then
    rm -rf "$repo/.git"
    echo "✓ $repo cloned and .git removed"
  else
    echo "✗ Failed to clone $repo"
  fi
done

echo "PaystackHQ cloning complete!"
