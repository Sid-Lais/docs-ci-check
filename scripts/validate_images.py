#!/usr/bin/env python3
"""
Validate image naming conventions.
All images must follow: AMNIC_DASHBOARD_NAME.{png|jpg|jpeg|gif}
"""

import os
import re
import sys
from pathlib import Path


class ImageValidator:
    # Pattern: AMNIC_DASHBOARD_NAME.ext (uppercase with underscores)
    IMAGE_NAME_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*\.(png|jpg|jpeg|gif)$')

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_image_name(self, file_path: str, filename: str) -> bool:
        """Validate image follows naming convention"""
        if not self.IMAGE_NAME_PATTERN.match(filename):
            error_msg = (
                f"❌ Invalid image name: '{filename}'\n"
                f"   Location: {file_path}\n"
                f"   Expected format: AMNIC_DASHBOARD_NAME.{{png|jpg|jpeg|gif}}\n"
                f"   Examples:\n"
                f"     - AMNIC_DASHBOARD_MAIN.png\n"
                f"     - AMNIC_DASHBOARD_SETTINGS_PAGE.jpg\n"
                f"     - AMNIC_WIDGET_ALERT_POPUP.gif"
            )
            self.errors.append(error_msg)
            return False
        return True

    def validate_directory(self, directory: str) -> bool:
        """Recursively validate all images in directory"""
        is_valid = True
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif'}

        if not os.path.exists(directory):
            return is_valid

        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in image_extensions:
                    file_path = os.path.join(root, file)
                    is_valid &= self.validate_image_name(file_path, file)

        return is_valid

    def generate_report(self) -> str:
        """Generate validation report"""
        if not self.errors and not self.warnings:
            return "✅ All image names are valid!\n"

        report = "# 🖼️ Image Validation Report\n\n"

        if self.errors:
            report += "## ❌ Naming Errors\n\n"
            for error in self.errors:
                report += f"{error}\n\n"

        if self.warnings:
            report += "## ⚠️ Warnings\n\n"
            for warning in self.warnings:
                report += f"{warning}\n\n"

        return report

def main():
    validator = ImageValidator()
    cwd = os.getcwd()

    # Validate images directory
    image_dir = os.path.join(cwd, 'images')
    validator.validate_directory(image_dir)

    # Also check assets directory for images
    assets_dir = os.path.join(cwd, 'assets')
    validator.validate_directory(assets_dir)

    report = validator.generate_report()
    print(report)

    if validator.errors:
        sys.exit(1)

    return 0

if __name__ == '__main__':
    sys.exit(main())
