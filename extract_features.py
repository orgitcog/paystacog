#!/usr/bin/env python3
"""
Feature Extraction and Cataloging Script
Analyzes all cloned repositories and extracts features for integration.
"""
import os
import json
from pathlib import Path
from collections import defaultdict

def analyze_repo(repo_path):
    """Analyze a single repository and extract its features."""
    features = {
        'name': os.path.basename(repo_path),
        'path': repo_path,
        'languages': [],
        'type': 'unknown',
        'features': [],
        'dependencies': [],
        'has_readme': False,
        'has_tests': False,
        'files': []
    }
    
    # Detect languages and file types
    lang_extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.php': 'PHP',
        '.java': 'Java',
        '.kt': 'Kotlin',
        '.swift': 'Swift',
        '.m': 'Objective-C',
        '.rb': 'Ruby',
        '.dart': 'Dart',
        '.vue': 'Vue',
        '.go': 'Go'
    }
    
    languages = set()
    important_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in lang_extensions:
                languages.add(lang_extensions[ext])
            
            # Track important files
            if file.lower() in ['readme.md', 'readme.txt', 'readme']:
                features['has_readme'] = True
            if 'test' in file.lower() or 'spec' in file.lower():
                features['has_tests'] = True
            if file in ['package.json', 'composer.json', 'requirements.txt', 
                       'Gemfile', 'build.gradle', 'pom.xml', 'Podfile',
                       'pubspec.yaml', 'setup.py']:
                important_files.append(os.path.join(root, file))
    
    features['languages'] = list(languages)
    features['files'] = important_files
    
    # Determine repo type
    name = features['name'].lower()
    if 'plugin-' in name:
        features['type'] = 'plugin'
        if 'wordpress' in name or 'woocommerce' in name or 'whmcs' in name:
            features['features'].append('wordpress-integration')
        if 'magento' in name:
            features['features'].append('magento-integration')
        if 'prestashop' in name:
            features['features'].append('prestashop-integration')
        if 'opencart' in name:
            features['features'].append('opencart-integration')
        if 'joomla' in name:
            features['features'].append('joomla-integration')
        if 'moodle' in name:
            features['features'].append('moodle-integration')
        if 'gravity' in name:
            features['features'].append('gravity-forms')
        if 'memberpress' in name or 'membership' in name:
            features['features'].append('membership-management')
    elif 'sample-' in name or name.startswith('sample'):
        features['type'] = 'sample'
        features['features'].append('reference-implementation')
    elif 'sdk' in name or name in ['paystack-android', 'paystack-ios', 'paystack-node', 'paystack-python', 'paystack_flutter']:
        features['type'] = 'sdk'
        features['features'].append('payment-integration')
    elif 'checkout' in name:
        features['type'] = 'checkout'
        features['features'].append('checkout-ui')
    elif 'cli' in name:
        features['type'] = 'cli'
        features['features'].append('command-line-interface')
    elif 'api' in name or 'openapi' in name:
        features['type'] = 'api'
        features['features'].append('api-specification')
    elif 'library' in name:
        features['type'] = 'library'
    elif 'documentation' in name or 'doc' in name:
        features['type'] = 'documentation'
    
    return features

def categorize_repos(repos):
    """Categorize repositories by type and feature."""
    categories = {
        'sdks': {'mobile': [], 'backend': [], 'frontend': []},
        'plugins': {'ecommerce': [], 'cms': [], 'lms': [], 'membership': []},
        'samples': {'web': [], 'mobile': [], 'backend': []},
        'tools': {'cli': [], 'api': [], 'documentation': []},
        'libraries': []
    }
    
    for repo in repos:
        name = repo['name'].lower()
        repo_type = repo['type']
        languages = repo['languages']
        
        # SDKs
        if repo_type == 'sdk':
            if any(l in languages for l in ['Java', 'Kotlin', 'Swift', 'Objective-C', 'Dart']):
                categories['sdks']['mobile'].append(repo)
            elif any(l in languages for l in ['Python', 'PHP', 'Ruby', 'Go']):
                categories['sdks']['backend'].append(repo)
            else:
                categories['sdks']['frontend'].append(repo)
        
        # Plugins
        elif repo_type == 'plugin':
            if any(f in repo['features'] for f in ['wordpress-integration', 'woocommerce-integration', 
                                                    'magento-integration', 'prestashop-integration', 
                                                    'opencart-integration']):
                categories['plugins']['ecommerce'].append(repo)
            elif any(f in repo['features'] for f in ['joomla-integration']):
                categories['plugins']['cms'].append(repo)
            elif any(f in repo['features'] for f in ['moodle-integration']):
                categories['plugins']['lms'].append(repo)
            elif any(f in repo['features'] for f in ['membership-management', 'gravity-forms']):
                categories['plugins']['membership'].append(repo)
            else:
                categories['plugins']['ecommerce'].append(repo)
        
        # Samples
        elif repo_type == 'sample':
            if any(l in languages for l in ['Java', 'Kotlin', 'Swift', 'Dart']):
                categories['samples']['mobile'].append(repo)
            elif any(l in languages for l in ['Vue', 'JavaScript', 'TypeScript']) and 'backend' not in name:
                categories['samples']['web'].append(repo)
            else:
                categories['samples']['backend'].append(repo)
        
        # Tools
        elif repo_type in ['cli', 'api', 'documentation']:
            categories['tools'][repo_type].append(repo)
        
        # Libraries
        elif repo_type == 'library':
            categories['libraries'].append(repo)
        
        # Checkout
        elif repo_type == 'checkout':
            if any(l in languages for l in ['Swift', 'Kotlin', 'Java']):
                categories['sdks']['mobile'].append(repo)
            else:
                categories['sdks']['frontend'].append(repo)
    
    return categories

def main():
    base_path = Path('/home/ubuntu/paystacog/integrations')
    
    all_repos = []
    
    # Analyze PaystackHQ repos
    hq_path = base_path / 'PaystackHQ'
    for repo_dir in hq_path.iterdir():
        if repo_dir.is_dir():
            repo_info = analyze_repo(str(repo_dir))
            repo_info['source'] = 'PaystackHQ'
            all_repos.append(repo_info)
    
    # Analyze PaystackOSS repos
    oss_path = base_path / 'PaystackOSS'
    for repo_dir in oss_path.iterdir():
        if repo_dir.is_dir():
            repo_info = analyze_repo(str(repo_dir))
            repo_info['source'] = 'PaystackOSS'
            all_repos.append(repo_info)
    
    # Categorize
    categories = categorize_repos(all_repos)
    
    # Generate report
    report = {
        'total_repos': len(all_repos),
        'by_source': {
            'PaystackHQ': len([r for r in all_repos if r['source'] == 'PaystackHQ']),
            'PaystackOSS': len([r for r in all_repos if r['source'] == 'PaystackOSS'])
        },
        'by_type': defaultdict(int),
        'by_language': defaultdict(int),
        'categories': categories,
        'all_repos': all_repos
    }
    
    for repo in all_repos:
        report['by_type'][repo['type']] += 1
        for lang in repo['languages']:
            report['by_language'][lang] += 1
    
    report['by_type'] = dict(report['by_type'])
    report['by_language'] = dict(report['by_language'])
    
    # Save report
    output_path = base_path.parent / 'feature_catalog.json'
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Feature catalog saved to {output_path}")
    print(f"\nTotal repositories: {report['total_repos']}")
    print(f"By source: {report['by_source']}")
    print(f"By type: {report['by_type']}")
    print(f"By language: {report['by_language']}")
    
    return report

if __name__ == '__main__':
    main()
