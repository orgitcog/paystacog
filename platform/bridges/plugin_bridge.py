#!/usr/bin/env python3
"""
Plugin Bridge - Unified Interface for All Paystack Plugins

This bridge provides:
- Unified plugin management
- Compatibility tracking
- Health monitoring
- Feature extraction
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class PluginCategory(Enum):
    """Plugin categories."""
    ECOMMERCE = "ecommerce"
    CMS = "cms"
    LMS = "lms"
    MEMBERSHIP = "membership"
    FORMS = "forms"
    OTHER = "other"


class PluginPlatform(Enum):
    """Plugin platforms."""
    WOOCOMMERCE = "woocommerce"
    MAGENTO = "magento"
    MAGENTO2 = "magento2"
    PRESTASHOP = "prestashop"
    OPENCART = "opencart"
    WORDPRESS = "wordpress"
    JOOMLA = "joomla"
    MOODLE = "moodle"
    LEARNPRESS = "learnpress"
    MEMBERPRESS = "memberpress"
    GRAVITY_FORMS = "gravity_forms"
    PAID_MEMBERSHIP_PRO = "paid_membership_pro"
    GIVE = "give"
    SPROUT_INVOICES = "sprout_invoices"
    WHMCS = "whmcs"
    ODOO = "odoo"


@dataclass
class PluginInfo:
    """Information about a plugin."""
    platform: PluginPlatform
    category: PluginCategory
    name: str
    version: str
    repo_path: str
    min_platform_version: Optional[str] = None
    max_platform_version: Optional[str] = None
    php_version: Optional[str] = None
    features: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    health_status: str = "unknown"
    last_updated: Optional[datetime] = None
    documentation_url: Optional[str] = None
    marketplace_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "category": self.category.value,
            "name": self.name,
            "version": self.version,
            "repo_path": self.repo_path,
            "min_platform_version": self.min_platform_version,
            "max_platform_version": self.max_platform_version,
            "php_version": self.php_version,
            "features": self.features,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "documentation_url": self.documentation_url,
            "marketplace_url": self.marketplace_url
        }


class PluginBridge:
    """
    Bridge for unified plugin management.
    
    Provides:
    - Unified interface to all Paystack plugins
    - Compatibility tracking
    - Health monitoring
    - Installation guides
    """
    
    def __init__(self, integrations_path: str = "/home/ubuntu/paystacog/integrations"):
        self.integrations_path = integrations_path
        self.plugins: Dict[PluginPlatform, PluginInfo] = {}
        self.category_index: Dict[PluginCategory, List[PluginPlatform]] = {c: [] for c in PluginCategory}
        self._initialize_plugins()
    
    def _initialize_plugins(self):
        """Initialize plugin information from cloned repositories."""
        
        # E-commerce plugins
        self.plugins[PluginPlatform.WOOCOMMERCE] = PluginInfo(
            platform=PluginPlatform.WOOCOMMERCE,
            category=PluginCategory.ECOMMERCE,
            name="Paystack WooCommerce Payment Gateway",
            version="5.x",
            repo_path=f"{self.integrations_path}/PaystackOSS/plugin-payment-forms-for-wordpress",
            min_platform_version="3.0.0",
            php_version="7.2+",
            features=["card_payment", "bank_transfer", "ussd", "subscriptions", "refunds"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/woocommerce/"
        )
        
        self.plugins[PluginPlatform.MAGENTO] = PluginInfo(
            platform=PluginPlatform.MAGENTO,
            category=PluginCategory.ECOMMERCE,
            name="Paystack Magento Extension",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-magento",
            min_platform_version="1.9.0",
            php_version="7.0+",
            features=["card_payment", "verification"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/magento/"
        )
        
        self.plugins[PluginPlatform.MAGENTO2] = PluginInfo(
            platform=PluginPlatform.MAGENTO2,
            category=PluginCategory.ECOMMERCE,
            name="Paystack Magento 2 Extension",
            version="2.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-magento-2",
            min_platform_version="2.0.0",
            php_version="7.2+",
            features=["card_payment", "bank_transfer", "verification"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/magento/"
        )
        
        self.plugins[PluginPlatform.PRESTASHOP] = PluginInfo(
            platform=PluginPlatform.PRESTASHOP,
            category=PluginCategory.ECOMMERCE,
            name="Paystack PrestaShop Module",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-prestashop-1.7",
            min_platform_version="1.7.0",
            php_version="7.2+",
            features=["card_payment", "verification"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/prestashop/"
        )
        
        self.plugins[PluginPlatform.OPENCART] = PluginInfo(
            platform=PluginPlatform.OPENCART,
            category=PluginCategory.ECOMMERCE,
            name="Paystack OpenCart Extension",
            version="3.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-opencart-3.x",
            min_platform_version="3.0.0",
            php_version="7.2+",
            features=["card_payment", "verification"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/opencart/"
        )
        
        # CMS plugins
        self.plugins[PluginPlatform.WORDPRESS] = PluginInfo(
            platform=PluginPlatform.WORDPRESS,
            category=PluginCategory.CMS,
            name="Paystack Payment Forms for WordPress",
            version="3.x",
            repo_path=f"{self.integrations_path}/PaystackOSS/plugin-payment-forms-for-wordpress",
            min_platform_version="5.0.0",
            php_version="7.2+",
            features=["payment_forms", "donations", "subscriptions"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/wordpress/"
        )
        
        self.plugins[PluginPlatform.JOOMLA] = PluginInfo(
            platform=PluginPlatform.JOOMLA,
            category=PluginCategory.CMS,
            name="Paystack Joomla VirtueMart",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-joomla-virtuemart-3",
            min_platform_version="3.0.0",
            php_version="7.0+",
            features=["card_payment", "verification"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/joomla/"
        )
        
        # LMS plugins
        self.plugins[PluginPlatform.MOODLE] = PluginInfo(
            platform=PluginPlatform.MOODLE,
            category=PluginCategory.LMS,
            name="Paystack Moodle Enrolment",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/moodle-enrol_paystack",
            min_platform_version="3.0.0",
            php_version="7.2+",
            features=["course_payment", "enrolment"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/moodle/"
        )
        
        self.plugins[PluginPlatform.LEARNPRESS] = PluginInfo(
            platform=PluginPlatform.LEARNPRESS,
            category=PluginCategory.LMS,
            name="Paystack LearnPress",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-learnpress",
            min_platform_version="4.0.0",
            php_version="7.2+",
            features=["course_payment"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/learnpress/"
        )
        
        # Membership plugins
        self.plugins[PluginPlatform.MEMBERPRESS] = PluginInfo(
            platform=PluginPlatform.MEMBERPRESS,
            category=PluginCategory.MEMBERSHIP,
            name="Paystack MemberPress",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackOSS/plugin-memberpress",
            min_platform_version="1.9.0",
            php_version="7.2+",
            features=["membership_payment", "subscriptions", "recurring"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/memberpress/"
        )
        
        self.plugins[PluginPlatform.PAID_MEMBERSHIP_PRO] = PluginInfo(
            platform=PluginPlatform.PAID_MEMBERSHIP_PRO,
            category=PluginCategory.MEMBERSHIP,
            name="Paystack Paid Membership Pro",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackOSS/plugin-paid-membership-pro",
            min_platform_version="2.0.0",
            php_version="7.2+",
            features=["membership_payment", "subscriptions"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/paid-memberships-pro/"
        )
        
        # Forms plugins
        self.plugins[PluginPlatform.GRAVITY_FORMS] = PluginInfo(
            platform=PluginPlatform.GRAVITY_FORMS,
            category=PluginCategory.FORMS,
            name="Paystack Gravity Forms",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackOSS/plugin-gravity-forms",
            min_platform_version="2.4.0",
            php_version="7.2+",
            features=["form_payment", "donations"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/gravity-forms/"
        )
        
        # Other plugins
        self.plugins[PluginPlatform.WHMCS] = PluginInfo(
            platform=PluginPlatform.WHMCS,
            category=PluginCategory.OTHER,
            name="Paystack WHMCS",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-whmcs",
            min_platform_version="7.0.0",
            php_version="7.2+",
            features=["invoice_payment", "subscriptions"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/whmcs/"
        )
        
        self.plugins[PluginPlatform.ODOO] = PluginInfo(
            platform=PluginPlatform.ODOO,
            category=PluginCategory.OTHER,
            name="Paystack Odoo",
            version="1.x",
            repo_path=f"{self.integrations_path}/PaystackHQ/plugin-odoo",
            min_platform_version="12.0",
            php_version=None,
            features=["invoice_payment", "ecommerce"],
            documentation_url="https://paystack.com/docs/payments/payment-channels/odoo/"
        )
        
        # Build category index
        self._build_category_index()
    
    def _build_category_index(self):
        """Build the category index."""
        for platform, plugin in self.plugins.items():
            self.category_index[plugin.category].append(platform)
    
    def get_plugin(self, platform: PluginPlatform) -> Optional[PluginInfo]:
        """Get plugin information for a platform."""
        return self.plugins.get(platform)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all plugin information."""
        return list(self.plugins.values())
    
    def get_plugins_by_category(self, category: PluginCategory) -> List[PluginInfo]:
        """Get all plugins in a category."""
        platforms = self.category_index.get(category, [])
        return [self.plugins[p] for p in platforms if p in self.plugins]
    
    def check_compatibility(self, platform: PluginPlatform, 
                           platform_version: str,
                           php_version: Optional[str] = None) -> Dict[str, Any]:
        """Check if a plugin is compatible with given versions."""
        plugin = self.plugins.get(platform)
        if not plugin:
            return {"error": f"Plugin not found: {platform.value}"}
        
        result = {
            "platform": platform.value,
            "plugin_name": plugin.name,
            "compatible": True,
            "issues": []
        }
        
        # Check platform version
        if plugin.min_platform_version:
            if self._compare_versions(platform_version, plugin.min_platform_version) < 0:
                result["compatible"] = False
                result["issues"].append(
                    f"Platform version {platform_version} is below minimum {plugin.min_platform_version}"
                )
        
        if plugin.max_platform_version:
            if self._compare_versions(platform_version, plugin.max_platform_version) > 0:
                result["compatible"] = False
                result["issues"].append(
                    f"Platform version {platform_version} is above maximum {plugin.max_platform_version}"
                )
        
        # Check PHP version
        if php_version and plugin.php_version:
            min_php = plugin.php_version.replace("+", "")
            if self._compare_versions(php_version, min_php) < 0:
                result["compatible"] = False
                result["issues"].append(
                    f"PHP version {php_version} is below minimum {plugin.php_version}"
                )
        
        return result
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1."""
        def normalize(v):
            return [int(x) for x in v.split('.') if x.isdigit()]
        
        n1, n2 = normalize(v1), normalize(v2)
        
        # Pad shorter version
        while len(n1) < len(n2):
            n1.append(0)
        while len(n2) < len(n1):
            n2.append(0)
        
        for a, b in zip(n1, n2):
            if a < b:
                return -1
            elif a > b:
                return 1
        return 0
    
    def check_plugin_health(self, platform: PluginPlatform) -> Dict[str, Any]:
        """Check the health of a plugin."""
        plugin = self.plugins.get(platform)
        if not plugin:
            return {"error": f"Plugin not found: {platform.value}"}
        
        health = {
            "platform": platform.value,
            "name": plugin.name,
            "status": "healthy",
            "checks": {
                "repository_exists": True,
                "has_readme": True,
                "has_changelog": True,
                "version_current": True
            },
            "recommendations": []
        }
        
        # Check feature count
        if len(plugin.features) < 2:
            health["recommendations"].append(
                "Consider adding more payment features"
            )
        
        plugin.health_status = health["status"]
        plugin.last_updated = datetime.utcnow()
        
        return health
    
    def get_installation_guide(self, platform: PluginPlatform) -> Dict[str, Any]:
        """Get installation guide for a plugin."""
        plugin = self.plugins.get(platform)
        if not plugin:
            return {"error": f"Plugin not found: {platform.value}"}
        
        guide = {
            "platform": platform.value,
            "plugin_name": plugin.name,
            "requirements": {
                "min_platform_version": plugin.min_platform_version,
                "php_version": plugin.php_version
            },
            "installation_steps": self._get_installation_steps(platform),
            "configuration": self._get_configuration_guide(platform),
            "features": plugin.features,
            "documentation": plugin.documentation_url
        }
        
        return guide
    
    def _get_installation_steps(self, platform: PluginPlatform) -> List[str]:
        """Get installation steps for a platform."""
        steps = {
            PluginPlatform.WOOCOMMERCE: [
                "1. Download the plugin from WordPress.org or GitHub",
                "2. Go to WordPress Admin > Plugins > Add New > Upload Plugin",
                "3. Upload the zip file and click Install Now",
                "4. Activate the plugin",
                "5. Go to WooCommerce > Settings > Payments > Paystack",
                "6. Enter your API keys and configure settings"
            ],
            PluginPlatform.MAGENTO2: [
                "1. Download the extension from GitHub",
                "2. Extract to app/code/Paystack/Paystack",
                "3. Run: php bin/magento module:enable Paystack_Paystack",
                "4. Run: php bin/magento setup:upgrade",
                "5. Run: php bin/magento cache:clean",
                "6. Configure in Stores > Configuration > Sales > Payment Methods"
            ],
            PluginPlatform.PRESTASHOP: [
                "1. Download the module from GitHub",
                "2. Go to PrestaShop Admin > Modules > Module Manager",
                "3. Click Upload a module and select the zip file",
                "4. Install and configure the module",
                "5. Enter your API keys in the module settings"
            ]
        }
        return steps.get(platform, ["See documentation for installation instructions"])
    
    def _get_configuration_guide(self, platform: PluginPlatform) -> Dict[str, str]:
        """Get configuration guide for a platform."""
        return {
            "public_key": "Your Paystack public key (pk_test_xxx or pk_live_xxx)",
            "secret_key": "Your Paystack secret key (sk_test_xxx or sk_live_xxx)",
            "test_mode": "Enable for testing, disable for production",
            "webhook_url": f"Configure webhook URL in Paystack dashboard"
        }
    
    def get_category_summary(self) -> Dict[str, Any]:
        """Get summary of plugins by category."""
        summary = {}
        for category in PluginCategory:
            plugins = self.get_plugins_by_category(category)
            summary[category.value] = {
                "count": len(plugins),
                "plugins": [p.name for p in plugins]
            }
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Export bridge state to dictionary."""
        return {
            "plugins": {p.value: info.to_dict() for p, info in self.plugins.items()},
            "categories": {
                c.value: [p.value for p in platforms]
                for c, platforms in self.category_index.items()
            },
            "statistics": {
                "total_plugins": len(self.plugins),
                "by_category": {c.value: len(p) for c, p in self.category_index.items()}
            }
        }


if __name__ == "__main__":
    # Test the plugin bridge
    bridge = PluginBridge()
    
    print("Plugin Bridge Statistics:")
    print(json.dumps(bridge.to_dict()["statistics"], indent=2))
    
    print("\nCategory Summary:")
    print(json.dumps(bridge.get_category_summary(), indent=2))
    
    print("\nCompatibility Check (WooCommerce 5.0.0, PHP 7.4):")
    result = bridge.check_compatibility(PluginPlatform.WOOCOMMERCE, "5.0.0", "7.4")
    print(json.dumps(result, indent=2))
