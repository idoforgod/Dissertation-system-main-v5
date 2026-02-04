#!/usr/bin/env python3
"""Validation Configuration Helper.

This module provides utilities for managing validation configuration
through environment variables, enabling opt-in validation without
modifying existing workflow code.

Design Principles:
- Opt-out: Validation is enabled by default
- Flexible: Can be disabled globally or per-session
- Non-invasive: Does not require code changes
- Documented: Clear guidance for users

Usage:
    # Enable validation for current session
    python3 validation_config.py --enable

    # Disable validation
    python3 validation_config.py --disable

    # Check current status
    python3 validation_config.py --status

    # Set fail-fast mode
    python3 validation_config.py --fail-fast true
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional
import json


# ============================================================================
# Environment Variables
# ============================================================================

ENV_VARS = {
    "USE_VALIDATION": {
        "description": "Enable validation layer",
        "default": "true",
        "valid_values": ["true", "false", "1", "0", "yes", "no"],
        "type": "boolean"
    },
    "FAIL_FAST": {
        "description": "Stop execution on first validation error",
        "default": "true",
        "valid_values": ["true", "false", "1", "0", "yes", "no"],
        "type": "boolean"
    },
    "VALIDATION_REPORT_DIR": {
        "description": "Directory for validation reports",
        "default": "validation-reports",
        "valid_values": None,
        "type": "string"
    },
    "VALIDATION_VERBOSE": {
        "description": "Enable verbose validation output",
        "default": "false",
        "valid_values": ["true", "false", "1", "0", "yes", "no"],
        "type": "boolean"
    }
}


# ============================================================================
# Configuration Class
# ============================================================================

class ValidationConfig:
    """Manage validation configuration through environment variables."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_file = Path.home() / ".thesis-orchestrator" / "validation.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, str]:
        """Load configuration from file.

        Returns:
            Dictionary of configuration values
        """
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, config: Dict[str, str]):
        """Save configuration to file.

        Args:
            config: Dictionary of configuration values
        """
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def get_env_value(self, key: str) -> Optional[str]:
        """Get environment variable value with fallback to config file.

        Args:
            key: Environment variable name

        Returns:
            Value from environment or config file, or default
        """
        # Priority: env var > config file > default
        if key in os.environ:
            return os.environ[key]

        config = self.load_config()
        if key in config:
            return config[key]

        if key in ENV_VARS:
            return ENV_VARS[key]["default"]

        return None

    def set_env_value(self, key: str, value: str, persistent: bool = True):
        """Set environment variable value.

        Args:
            key: Environment variable name
            value: Value to set
            persistent: If True, save to config file
        """
        # Validate
        if key in ENV_VARS:
            valid_values = ENV_VARS[key]["valid_values"]
            if valid_values and value not in valid_values:
                raise ValueError(
                    f"Invalid value '{value}' for {key}. "
                    f"Valid values: {', '.join(valid_values)}"
                )

        # Set in environment
        os.environ[key] = value

        # Save to config file if persistent
        if persistent:
            config = self.load_config()
            config[key] = value
            self.save_config(config)

    def enable_validation(self, fail_fast: bool = True):
        """Enable validation with specified options.

        Args:
            fail_fast: Enable fail-fast mode
        """
        self.set_env_value("USE_VALIDATION", "true")
        self.set_env_value("FAIL_FAST", "true" if fail_fast else "false")

        print("✅ Validation enabled")
        print(f"   Fail-fast: {'enabled' if fail_fast else 'disabled'}")

    def disable_validation(self):
        """Disable validation."""
        self.set_env_value("USE_VALIDATION", "false")

        print("⏭️  Validation disabled")
        print("   Using standard workflow (no validation)")

    def is_validation_enabled(self) -> bool:
        """Check if validation is enabled.

        Returns:
            True if validation is enabled
        """
        value = self.get_env_value("USE_VALIDATION")
        return value.lower() in ["true", "1", "yes"] if value else False

    def is_fail_fast_enabled(self) -> bool:
        """Check if fail-fast mode is enabled.

        Returns:
            True if fail-fast is enabled
        """
        value = self.get_env_value("FAIL_FAST")
        return value.lower() in ["true", "1", "yes"] if value else True

    def get_report_dir(self) -> str:
        """Get validation report directory.

        Returns:
            Report directory path
        """
        return self.get_env_value("VALIDATION_REPORT_DIR") or "validation-reports"

    def is_verbose_enabled(self) -> bool:
        """Check if verbose mode is enabled.

        Returns:
            True if verbose mode is enabled
        """
        value = self.get_env_value("VALIDATION_VERBOSE")
        return value.lower() in ["true", "1", "yes"] if value else False

    def print_status(self):
        """Print current configuration status."""
        print("\n" + "="*70)
        print("Validation Configuration Status")
        print("="*70 + "\n")

        print(f"Validation:     {'✅ ENABLED' if self.is_validation_enabled() else '⏭️  DISABLED'}")
        print(f"Fail-fast:      {'✅ ENABLED' if self.is_fail_fast_enabled() else '⏭️  DISABLED'}")
        print(f"Verbose:        {'✅ ENABLED' if self.is_verbose_enabled() else '⏭️  DISABLED'}")
        print(f"Report Dir:     {self.get_report_dir()}")
        print(f"\nConfig File:    {self.config_file}")

        if self.config_file.exists():
            print(f"Status:         Configured")
        else:
            print(f"Status:         Using defaults")

        print("\n" + "="*70 + "\n")

    def print_help(self):
        """Print help information."""
        print("\n" + "="*70)
        print("Validation Environment Variables")
        print("="*70 + "\n")

        for var, info in ENV_VARS.items():
            print(f"{var}:")
            print(f"  Description: {info['description']}")
            print(f"  Default:     {info['default']}")
            if info['valid_values']:
                print(f"  Valid:       {', '.join(info['valid_values'])}")
            print()

        print("="*70)
        print("Usage Examples:")
        print("="*70)
        print()
        print("# Enable validation with fail-fast")
        print("export USE_VALIDATION=true")
        print("export FAIL_FAST=true")
        print()
        print("# Disable validation")
        print("export USE_VALIDATION=false")
        print()
        print("# Enable verbose output")
        print("export VALIDATION_VERBOSE=true")
        print()
        print("# Change report directory")
        print("export VALIDATION_REPORT_DIR=my-reports")
        print()
        print("="*70 + "\n")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for validation configuration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage thesis workflow validation configuration"
    )
    parser.add_argument("--enable", action="store_true",
                       help="Enable validation")
    parser.add_argument("--disable", action="store_true",
                       help="Disable validation")
    parser.add_argument("--fail-fast", type=str, choices=["true", "false"],
                       help="Set fail-fast mode")
    parser.add_argument("--verbose", type=str, choices=["true", "false"],
                       help="Set verbose mode")
    parser.add_argument("--report-dir", type=str,
                       help="Set report directory")
    parser.add_argument("--status", action="store_true",
                       help="Show current configuration")
    parser.add_argument("--help-vars", action="store_true",
                       help="Show help for environment variables")

    args = parser.parse_args()

    config = ValidationConfig()

    if args.help_vars:
        config.print_help()
        return 0

    if args.enable:
        fail_fast = args.fail_fast != "false" if args.fail_fast else True
        config.enable_validation(fail_fast)

    if args.disable:
        config.disable_validation()

    if args.fail_fast:
        config.set_env_value("FAIL_FAST", args.fail_fast)
        print(f"✅ Fail-fast {'enabled' if args.fail_fast == 'true' else 'disabled'}")

    if args.verbose:
        config.set_env_value("VALIDATION_VERBOSE", args.verbose)
        print(f"✅ Verbose mode {'enabled' if args.verbose == 'true' else 'disabled'}")

    if args.report_dir:
        config.set_env_value("VALIDATION_REPORT_DIR", args.report_dir)
        print(f"✅ Report directory set to: {args.report_dir}")

    if args.status or not any([args.enable, args.disable, args.fail_fast,
                               args.verbose, args.report_dir, args.help_vars]):
        config.print_status()

    return 0


if __name__ == "__main__":
    sys.exit(main())
