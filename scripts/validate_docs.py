#!/usr/bin/env python3
"""
Main documentation validation script.
Checks for:
1. Proper image and doc naming conventions
2. Component context references (Vantage, Cloudzero)
3. Placeholder formatting
4. Missing assets
5. Draft/TODO markers
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


class DocValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.valid_components = ['Vantage', 'Cloudzero', 'AWS', 'GCP', 'Azure']
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif'}

    # Image naming: AMNIC_DASHBOARD_NAME.ext
    IMAGE_NAME_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*\.(png|jpg|jpeg|gif)$')

    # Placeholder format: [PLACEHOLDER IMAGE/TABLE/CONTENT NAME_OF_CONTENT]
    PLACEHOLDER_PATTERN = re.compile(r'\[PLACEHOLDER\s+(IMAGE|TABLE|CONTENT)\s+[A-Z0-9_]+\]')

    # Draft/TODO format: [DRAFT/TO-DO, CHANGE]
    DRAFT_PATTERN = re.compile(r'\[DRAFT/TO-DO,?\s*CHANGE\]')

    def validate_image_names(self, file_path: str) -> bool:
        """Validate that image follows naming convention: AMNIC_DASHBOARD_NAME.ext"""
        filename = os.path.basename(file_path)

        if not self.IMAGE_NAME_PATTERN.match(filename):
            self.errors.append(
                f"❌ Image naming invalid: '{filename}'\n"
                f"   Expected format: AMNIC_DASHBOARD_NAME.{{png|jpg|jpeg|gif}}\n"
                f"   Example: AMNIC_DASHBOARD_MAIN.png"
            )
            return False
        return True

    def check_placeholders_in_content(self, file_path: str, content: str) -> bool:
        """Check if placeholders follow proper format"""
        is_valid = True
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Check for malformed placeholders
            if '[PLACEHOLDER' in line.upper():
                if not self.PLACEHOLDER_PATTERN.search(line):
                    self.errors.append(
                        f"❌ Malformed placeholder in {file_path}:{line_num}\n"
                        f"   Found: {line.strip()}\n"
                        f"   Expected format: [PLACEHOLDER IMAGE/TABLE/CONTENT NAME_OF_CONTENT]"
                    )
                    is_valid = False

            # Check for placeholder leftovers
            if '{{' in line or '}}' in line or '###' in line.upper():
                if 'PLACEHOLDER' not in line and 'TODO' not in line:
                    self.warnings.append(
                        f"⚠️ Possible unresolved placeholder in {file_path}:{line_num}\n"
                        f"   {line.strip()}"
                    )

        return is_valid

    def check_draft_markers(self, file_path: str, content: str) -> bool:
        """Check for [DRAFT/TO-DO, CHANGE] markers"""
        is_valid = True
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            if '[DRAFT' in line or '[TO-DO' in line or 'CHANGE]' in line:
                if not self.DRAFT_PATTERN.search(line):
                    self.warnings.append(
                        f"⚠️ Possible incomplete draft marker in {file_path}:{line_num}\n"
                        f"   Found: {line.strip()}\n"
                        f"   Expected format: [DRAFT/TO-DO, CHANGE]"
                    )
                else:
                    self.errors.append(
                        f"❌ Unresolved DRAFT marker found in {file_path}:{line_num}\n"
                        f"   {line.strip()}"
                    )
                    is_valid = False

        return is_valid

    def validate_component_references(self, file_path: str, content: str) -> bool:
        """Validate component references are properly formatted"""
        is_valid = True
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for component in self.valid_components:
                if component in line:
                    # Check if component name is properly contextualized
                    # Should not appear as random text, should have description nearby
                    if line.strip().startswith(component):
                        context_check = line.count(' ') > 2
                        if not context_check:
                            self.warnings.append(
                                f"⚠️ Bare component reference in {file_path}:{line_num}\n"
                                f"   '{component}' should have context/description"
                            )

        return is_valid

    def check_missing_assets(self, file_path: str, content: str) -> bool:
        """Check for referenced images that don't exist"""
        is_valid = True
        base_dir = os.path.dirname(file_path)

        # Find image references in markdown
        # Patterns: ![alt](path/image.png) or [link](path/image.png)
        image_refs = re.findall(r'\!\?\[.*?\]\((.*?)\)', content)
        image_refs.extend(re.findall(r'\[.*?\]\((.*?\.(?:png|jpg|jpeg|gif))\)', content))

        for img_ref in image_refs:
            # Skip external URLs
            if img_ref.startswith(('http://', 'https://', 'www.')):
                continue

            # Check if file exists
            full_path = os.path.join(base_dir, img_ref)
            if not os.path.exists(full_path):
                self.errors.append(
                    f"❌ Referenced asset not found in {file_path}\n"
                    f"   Missing: {img_ref}"
                )
                is_valid = False

        return is_valid

    def validate_file(self, file_path: str) -> bool:
        """Validate a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"❌ Failed to read {file_path}: {str(e)}")
            return False

        file_ext = os.path.splitext(file_path)[1].lower()
        is_valid = True

        # Image validation
        if file_ext in self.image_extensions:
            is_valid &= self.validate_image_names(file_path)

        # Document validation
        if file_ext in {'.md', '.markdown'}:
            is_valid &= self.check_placeholders_in_content(file_path, content)
            is_valid &= self.check_draft_markers(file_path, content)
            is_valid &= self.validate_component_references(file_path, content)
            is_valid &= self.check_missing_assets(file_path, content)

        return is_valid

    def validate_directory(self, directory: str) -> bool:
        """Recursively validate all files in directory"""
        is_valid = True
        valid_dirs = ['docs', 'assets', 'images']

        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                # Only validate relevant files
                if file_ext in {'.md', '.markdown', '.png', '.jpg', '.jpeg', '.gif'}:
                    is_valid &= self.validate_file(file_path)

        return is_valid

    def generate_report(self) -> str:
        """Generate validation report"""
        report = "# 📋 Documentation Validation Report\n\n"

        if not self.errors and not self.warnings:
            report += "✅ All checks passed!\n"
            return report

        if self.errors:
            report += "## ❌ Errors\n\n"
            for error in self.errors:
                report += f"- {error}\n\n"

        if self.warnings:
            report += "## ⚠️ Warnings\n\n"
            for warning in self.warnings:
                report += f"- {warning}\n\n"

        return report

def main():
    validator = DocValidator()

    # Get current working directory
    cwd = os.getcwd()

    # Validate docs, assets, and images directories
    for directory in ['docs', 'assets', 'images']:
        dir_path = os.path.join(cwd, directory)
        if os.path.exists(dir_path):
            validator.validate_directory(dir_path)

    # Generate report
    report = validator.generate_report()

    # Write report
    with open('validation_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(report)

    # Write failure marker if there are errors
    if validator.errors:
        with open('validation_failed.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(validator.errors))
        sys.exit(1)

    return 0

if __name__ == '__main__':
    sys.exit(main())
