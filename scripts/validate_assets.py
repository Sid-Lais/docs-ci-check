#!/usr/bin/env python3
"""
Validate asset references and check for missing files.
Ensures all referenced assets exist and are accessible.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


class AssetValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.referenced_assets = {}
        self.existing_assets = set()

    def find_existing_assets(self, root_dir: str):
        """Build a set of all existing assets"""
        asset_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',  # Images
            '.pdf', '.xlsx', '.xls', '.csv', '.json', '.yaml'  # Documents
        }

        for directory in ['assets', 'images', 'docs']:
            dir_path = os.path.join(root_dir, directory)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext in asset_extensions:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, root_dir)
                            self.existing_assets.add(rel_path.replace('\\', '/'))

    def extract_asset_references(self, file_path: str, content: str):
        """Extract all asset references from markdown content"""
        # Markdown image: ![alt](path/to/image.ext)
        image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)

        # Markdown link: [text](path/to/file.ext)
        link_refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        # HTML img tags: <img src="path/to/image.ext" ...>
        html_img_refs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)

        # HTML link tags: <a href="path/to/file.ext">
        html_link_refs = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', content, re.IGNORECASE)

        all_refs = []
        for ref in image_refs + link_refs + html_img_refs + html_link_refs:
            if isinstance(ref, tuple):
                path = ref[1] if len(ref) > 1 else ref[0]
            else:
                path = ref

            # Skip external URLs
            if path.startswith(('http://', 'https://', 'www.', 'mailto:', '#')):
                continue

            all_refs.append((file_path, path))

        return all_refs

    def validate_asset_references(self, root_dir: str):
        """Check if all referenced assets exist"""
        docs_dir = os.path.join(root_dir, 'docs')

        if not os.path.exists(docs_dir):
            return

        for root, dirs, files in os.walk(docs_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        refs = self.extract_asset_references(file_path, content)

                        for doc_path, asset_ref in refs:
                            # Resolve relative path
                            if asset_ref.startswith('/'):
                                # Absolute from root
                                normalized = asset_ref.lstrip('/')
                            else:
                                # Relative to document
                                doc_dir = os.path.dirname(doc_path)
                                full_path = os.path.normpath(
                                    os.path.join(doc_dir, asset_ref)
                                )
                                normalized = os.path.relpath(full_path, root_dir)

                            normalized = normalized.replace('\\', '/')

                            # Check if asset exists
                            if normalized not in self.existing_assets:
                                # Check if it exists as actual file for case-insensitive systems
                                full_check = os.path.join(root_dir, normalized)
                                if not os.path.exists(full_check):
                                    rel_doc = os.path.relpath(doc_path, root_dir)
                                    self.errors.append(
                                        f"❌ Missing asset reference in {rel_doc}\n"
                                        f"   Referenced: {asset_ref}\n"
                                        f"   Resolved to: {normalized}\n"
                                        f"   File does not exist in assets/images/docs directories"
                                    )

                    except Exception as e:
                        self.errors.append(f"❌ Error reading {file_path}: {str(e)}")

    def check_asset_usage(self, root_dir: str):
        """Check for unused assets (optional warning)"""
        used_assets = set()

        for directory in ['docs']:
            dir_path = os.path.join(root_dir, directory)
            if not os.path.exists(dir_path):
                continue

            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith(('.md', '.markdown')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            refs = self.extract_asset_references(file_path, content)
                            for _, asset in refs:
                                used_assets.add(asset)
                        except:
                            pass

        # Find unused assets (optional)
        for asset in self.existing_assets:
            if asset not in used_assets:
                # Only warn about images, not all assets
                if asset.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    self.warnings.append(
                        f"⚠️ Unused asset: {asset}\n"
                        f"   This file is in the assets/images directory but not referenced in any documentation."
                    )

    def generate_report(self) -> str:
        """Generate asset validation report"""
        if not self.errors and not self.warnings:
            return "✅ All asset references are valid!\n"

        report = "# 📦 Asset Validation Report\n\n"

        if self.errors:
            report += "## ❌ Missing Assets\n\n"
            for error in self.errors:
                report += f"{error}\n\n"

        if self.warnings:
            report += "## ⚠️ Unused Assets\n\n"
            for warning in self.warnings:
                report += f"{warning}\n\n"

        return report

def main():
    validator = AssetValidator()
    cwd = os.getcwd()

    # Find all existing assets
    validator.find_existing_assets(cwd)

    # Validate all references
    validator.validate_asset_references(cwd)

    # Check for unused assets
    validator.check_asset_usage(cwd)

    report = validator.generate_report()
    print(report)

    if validator.errors:
        sys.exit(1)

    return 0

if __name__ == '__main__':
    sys.exit(main())
