#!/usr/bin/env python3
"""
Strict content gate for documentation.

Blocks merge when any of the following are present:
1) Any placeholder marker (e.g. [PLACEHOLDER ...])
2) Any draft marker (e.g. [DRAFT/TO-DO, CHANGE])
3) Forbidden words (case-insensitive): Vantage, Cloudzero, finout
"""

import os
import re
import sys
from pathlib import Path


class PlaceholderChecker:
    ANY_PLACEHOLDER = re.compile(r'\[PLACEHOLDER[^\]]*\]', re.IGNORECASE)
    ANY_DRAFT = re.compile(r'\[(?:DRAFT|TO-DO)[^\]]*\]', re.IGNORECASE)
    FORBIDDEN_WORDS = ('vantage', 'cloudzero', 'finout')

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
        """Check for blocked content in file"""
        is_valid = True
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            placeholders = self.ANY_PLACEHOLDER.findall(line)
            for placeholder in placeholders:
                self.errors.append(
                    f"❌ Unresolved placeholder in {file_path}:{line_num}\n"
                    f"   Found: {placeholder}\n"
                    f"   Any placeholder blocks merge. Replace with final content."
                )
                is_valid = False

            drafts = self.ANY_DRAFT.findall(line)
            for draft_marker in drafts:
                self.errors.append(
                    f"❌ Unresolved draft marker in {file_path}:{line_num}\n"
                    f"   Found: {draft_marker}\n"
                    f"   Draft markers block merge until removed."
                )
                is_valid = False

            for forbidden in self.FORBIDDEN_WORDS:
                for _ in re.finditer(rf'\b{re.escape(forbidden)}\b', line, flags=re.IGNORECASE):
                    self.errors.append(
                        f"❌ Forbidden word in {file_path}:{line_num}\n"
                        f"   Found: {forbidden}\n"
                        f"   Remove or replace forbidden terms before merging."
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
        """Generate policy check report"""
        if not self.errors and not self.warnings:
            return "✅ No blocked placeholders, draft markers, or forbidden words found!\n"

        report = "# 📌 Placeholder and Forbidden Word Check Report\n\n"

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

    # Check entire repository markdown content
    checker.check_directory(cwd)

    report = checker.generate_report()
    print(report)

    if checker.errors:
        sys.exit(1)

    return 0

if __name__ == '__main__':
    sys.exit(main())
