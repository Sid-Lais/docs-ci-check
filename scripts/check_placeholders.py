#!/usr/bin/env python3
"""
Check for unresolved placeholders in documentation.
Valid formats:
  - [PLACEHOLDER IMAGE NAME_OF_CONTENT]
  - [PLACEHOLDER TABLE NAME_OF_CONTENT]
  - [PLACEHOLDER CONTENT NAME_OF_CONTENT]
  - [DRAFT/TO-DO, CHANGE]
"""

import os
import re
import sys
from pathlib import Path


class PlaceholderChecker:
    # Valid placeholder format: [PLACEHOLDER TYPE NAME]
    VALID_PLACEHOLDER = re.compile(r'^\[PLACEHOLDER\s+(IMAGE|TABLE|CONTENT)\s+[A-Z0-9_]+\]$')

    # Valid draft format: [DRAFT/TO-DO, CHANGE]
    VALID_DRAFT = re.compile(r'^\[DRAFT/TO-DO,?\s*CHANGE\]$')

    # Common invalid patterns
    INVALID_PATTERNS = [
        (r'{{.*?}}', 'Mustache template syntax'),
        (r'\[\[\s*\w+\s*\]\]', 'Double bracket placeholder'),
        (r'<TODO.*?>', 'HTML TODO comment'),
        (r'<!--\s*TODO.*?-->', 'HTML comment TODO'),
        (r'FIXME', 'FIXME without proper format'),
        (r'XXX\s', 'XXX marker without proper format'),
        (r'\[TBD\]', 'TBD without proper format'),
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_placeholders_in_file(self, file_path: str, content: str) -> bool:
        """Check for unresolved placeholders in file"""
        is_valid = True
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Check for PLACEHOLDER patterns
            placeholders = re.findall(r'\[PLACEHOLDER[^\]]*\]', line, re.IGNORECASE)
            for placeholder in placeholders:
                if not self.VALID_PLACEHOLDER.search(placeholder):
                    self.errors.append(
                        f"❌ Invalid placeholder format in {file_path}:{line_num}\n"
                        f"   Found: {placeholder}\n"
                        f"   Expected: [PLACEHOLDER IMAGE/TABLE/CONTENT NAME_OF_ITEM]\n"
                        f"   Example: [PLACEHOLDER IMAGE DASHBOARD_SCREENSHOT]"
                    )
                    is_valid = False

            # Check for DRAFT patterns
            if re.search(r'\[DRAFT|\[TO-DO|CHANGE\]', line, re.IGNORECASE):
                if not self.VALID_DRAFT.search(line.strip()):
                    self.errors.append(
                        f"❌ Invalid draft marker in {file_path}:{line_num}\n"
                        f"   Found: {line.strip()}\n"
                        f"   Expected: [DRAFT/TO-DO, CHANGE]\n"
                        f"   (This indicates incomplete work that shouldn't be merged)"
                    )
                    is_valid = False
                else:
                    # Valid draft marker found - should not be in production
                    self.errors.append(
                        f"❌ Unresolved DRAFT marker in {file_path}:{line_num}\n"
                        f"   {line.strip()}\n"
                        f"   Please resolve or remove before merging."
                    )
                    is_valid = False

            # Check for invalid patterns
            for pattern, description in self.INVALID_PATTERNS:
                if re.search(pattern, line):
                    self.warnings.append(
                        f"⚠️ Possible unresolved placeholder in {file_path}:{line_num}\n"
                        f"   Pattern: {description}\n"
                        f"   Line: {line.strip()}"
                    )

        return is_valid

    def check_directory(self, directory: str) -> bool:
        """Recursively check all markdown files"""
        is_valid = True

        if not os.path.exists(directory):
            return is_valid

        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        is_valid &= self.check_placeholders_in_file(file_path, content)
                    except Exception as e:
                        self.errors.append(f"❌ Error reading {file_path}: {str(e)}")
                        is_valid = False

        return is_valid

    def generate_report(self) -> str:
        """Generate placeholder check report"""
        if not self.errors and not self.warnings:
            return "✅ No unresolved placeholders found!\n"

        report = "# 📌 Placeholder Check Report\n\n"

        if self.errors:
            report += "## ❌ Critical Issues\n\n"
            for error in self.errors:
                report += f"{error}\n\n"

        if self.warnings:
            report += "## ⚠️ Warnings\n\n"
            for warning in self.warnings:
                report += f"{warning}\n\n"

        return report

def main():
    checker = PlaceholderChecker()
    cwd = os.getcwd()

    # Check docs directory
    docs_dir = os.path.join(cwd, 'docs')
    checker.check_directory(docs_dir)

    report = checker.generate_report()
    print(report)

    if checker.errors:
        sys.exit(1)

    return 0

if __name__ == '__main__':
    sys.exit(main())
