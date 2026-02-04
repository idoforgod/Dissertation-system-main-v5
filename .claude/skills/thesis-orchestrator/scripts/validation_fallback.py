#!/usr/bin/env python3
"""Automatic Fallback System for Validation.

This module provides automatic fallback mechanisms when validation system
encounters errors. It ensures that workflow can continue even if validation
fails, providing a safety net for users.

Design Principles:
- Safety First: Never block user's work due to validation errors
- Transparent: Log when fallback occurs
- Automatic: No user intervention required
- Recoverable: Can retry validation later

Usage:
    from validation_fallback import with_fallback

    @with_fallback
    def my_validated_function():
        # If this fails, automatically falls back to standard execution
        validator.enforce_step(115)
        return result
"""

import os
import sys
from pathlib import Path
from typing import Callable, Any, Optional
from datetime import datetime
import json
import traceback
from functools import wraps


# ============================================================================
# Fallback Logger
# ============================================================================

class FallbackLogger:
    """Logs fallback events for debugging and monitoring."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize fallback logger.

        Args:
            log_dir: Directory for fallback logs (default: ~/.thesis-orchestrator/fallback-logs)
        """
        if log_dir is None:
            log_dir = Path.home() / ".thesis-orchestrator" / "fallback-logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.log_dir / f"fallback-{datetime.now().strftime('%Y%m%d')}.log"

    def log_fallback(
        self,
        reason: str,
        function_name: str,
        error: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        """Log a fallback event.

        Args:
            reason: Why fallback occurred
            function_name: Name of function that failed
            error: Exception that caused fallback
            context: Additional context information
        """
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "function": function_name,
            "reason": reason,
            "error": str(error) if error else None,
            "error_type": type(error).__name__ if error else None,
            "context": context or {}
        }

        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

        # Also print to stderr for visibility
        print(f"\n⚠️  FALLBACK TRIGGERED: {reason}", file=sys.stderr)
        print(f"   Function: {function_name}", file=sys.stderr)
        if error:
            print(f"   Error: {error}", file=sys.stderr)
        print(f"   → Falling back to standard execution\n", file=sys.stderr)

    def get_recent_fallbacks(self, limit: int = 10) -> list:
        """Get recent fallback events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent fallback events
        """
        if not self.log_file.exists():
            return []

        fallbacks = []
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    fallbacks.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return fallbacks[-limit:]

    def count_fallbacks_today(self) -> int:
        """Count fallback events today.

        Returns:
            Number of fallback events today
        """
        today = datetime.now().strftime('%Y%m%d')
        log_file = self.log_dir / f"fallback-{today}.log"

        if not log_file.exists():
            return 0

        with open(log_file, 'r') as f:
            return sum(1 for _ in f)


# ============================================================================
# Validation Health Check
# ============================================================================

class ValidationHealthCheck:
    """Checks if validation system is healthy."""

    @staticmethod
    def check_validation_modules() -> tuple[bool, list[str]]:
        """Check if validation modules can be imported.

        Returns:
            (is_healthy, missing_modules)
        """
        required_modules = [
            'workflow_validator',
            'validated_executor',
            'phase_validator'
        ]

        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)

        is_healthy = len(missing) == 0
        return is_healthy, missing

    @staticmethod
    def check_working_directory(working_dir: Path) -> bool:
        """Check if working directory is valid.

        Args:
            working_dir: Path to check

        Returns:
            True if valid
        """
        if not working_dir.exists():
            return False

        # Check basic structure
        required_dirs = ["00-session", "01-literature", "02-research-design",
                        "03-thesis", "04-publication"]

        # At least session directory should exist
        return (working_dir / "00-session").exists()

    @staticmethod
    def check_validation_health() -> dict:
        """Comprehensive health check.

        Returns:
            Dictionary with health status
        """
        health = {
            "overall": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }

        # Check 1: Modules
        modules_ok, missing = ValidationHealthCheck.check_validation_modules()
        health["checks"]["modules"] = {
            "status": "pass" if modules_ok else "fail",
            "missing": missing
        }
        if not modules_ok:
            health["overall"] = "unhealthy"

        # Check 2: Environment
        env_vars = {
            "USE_VALIDATION": os.environ.get("USE_VALIDATION", "not set"),
            "FAIL_FAST": os.environ.get("FAIL_FAST", "not set"),
        }
        health["checks"]["environment"] = {
            "status": "pass",
            "variables": env_vars
        }

        # Check 3: Fallback logs
        logger = FallbackLogger()
        fallback_count = logger.count_fallbacks_today()
        health["checks"]["fallbacks_today"] = {
            "status": "warning" if fallback_count > 5 else "pass",
            "count": fallback_count
        }
        if fallback_count > 10:
            health["overall"] = "degraded"

        return health


# ============================================================================
# Fallback Decorator
# ============================================================================

def with_fallback(
    fallback_function: Optional[Callable] = None,
    log: bool = True,
    raise_on_fallback: bool = False
):
    """Decorator that adds automatic fallback to a function.

    If the decorated function raises an exception, automatically
    falls back to standard execution.

    Args:
        fallback_function: Alternative function to call on failure
        log: Whether to log fallback events
        raise_on_fallback: Whether to raise exception after fallback

    Usage:
        @with_fallback
        def validated_function():
            validator.enforce_step(115)
            return execute_agent()

        # If validation fails, function continues without validation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Try validated execution
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log fallback event
                if log:
                    logger = FallbackLogger()
                    logger.log_fallback(
                        reason="Validation function raised exception",
                        function_name=func.__name__,
                        error=e,
                        context={
                            "args": str(args),
                            "kwargs": str(kwargs),
                            "traceback": traceback.format_exc()
                        }
                    )

                # Execute fallback
                if fallback_function:
                    try:
                        print(f"⚠️  Executing fallback function...", file=sys.stderr)
                        result = fallback_function(*args, **kwargs)
                        print(f"✅ Fallback execution succeeded", file=sys.stderr)
                        return result
                    except Exception as fallback_error:
                        print(f"❌ Fallback also failed: {fallback_error}", file=sys.stderr)
                        if raise_on_fallback:
                            raise
                        return None
                else:
                    # No fallback function provided - just log and optionally raise
                    if raise_on_fallback:
                        raise
                    return None

        return wrapper
    return decorator


# ============================================================================
# Safe Execution Wrapper
# ============================================================================

class SafeValidatedExecutor:
    """Wrapper for ValidatedExecutor with automatic fallback.

    This wraps the ValidatedExecutor to provide automatic fallback
    to standard execution if validation fails.
    """

    def __init__(self, working_dir: Path, fail_fast: bool = True):
        """Initialize safe executor.

        Args:
            working_dir: Working directory
            fail_fast: Whether to fail fast on validation errors
        """
        self.working_dir = Path(working_dir)
        self.fail_fast = fail_fast
        self.logger = FallbackLogger()

        # Try to import and initialize ValidatedExecutor
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from validated_executor import ValidatedExecutor
            self.executor = ValidatedExecutor(working_dir, fail_fast)
            self.validation_available = True
        except Exception as e:
            self.logger.log_fallback(
                reason="Failed to initialize ValidatedExecutor",
                function_name="SafeValidatedExecutor.__init__",
                error=e
            )
            self.executor = None
            self.validation_available = False

    def execute_step(
        self,
        step: int,
        agent_function: Callable,
        agent_name: str,
        skip_pre_validation: bool = False,
        skip_post_validation: bool = False
    ) -> Any:
        """Execute step with automatic fallback.

        If validation fails, automatically falls back to standard execution.

        Args:
            step: Step number
            agent_function: Agent to execute
            agent_name: Agent name
            skip_pre_validation: Skip pre-validation
            skip_post_validation: Skip post-validation

        Returns:
            Execution result
        """
        if not self.validation_available:
            # Validation not available - use standard execution
            print(f"⚠️  Validation not available, using standard execution", file=sys.stderr)
            return agent_function()

        try:
            # Try validated execution
            return self.executor.execute_step(
                step=step,
                agent_function=agent_function,
                agent_name=agent_name,
                skip_pre_validation=skip_pre_validation,
                skip_post_validation=skip_post_validation
            )
        except Exception as e:
            # Validation failed - fallback to standard execution
            self.logger.log_fallback(
                reason="Validated execution failed",
                function_name=f"execute_step_{step}",
                error=e,
                context={"step": step, "agent_name": agent_name}
            )

            print(f"\n⚠️  Validation failed for step {step}, falling back to standard execution", file=sys.stderr)
            print(f"   Error: {e}", file=sys.stderr)
            print(f"   → Executing {agent_name} without validation\n", file=sys.stderr)

            # Execute without validation
            try:
                result = agent_function()
                print(f"✅ Standard execution succeeded for step {step}", file=sys.stderr)
                return result
            except Exception as agent_error:
                print(f"❌ Standard execution also failed: {agent_error}", file=sys.stderr)
                raise


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for fallback management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage validation fallback system")
    parser.add_argument("--health", action="store_true",
                       help="Check validation system health")
    parser.add_argument("--recent", type=int, default=10,
                       help="Show recent fallback events")
    parser.add_argument("--count", action="store_true",
                       help="Count fallbacks today")
    parser.add_argument("--clear-logs", action="store_true",
                       help="Clear fallback logs")

    args = parser.parse_args()

    if args.health:
        # Health check
        health = ValidationHealthCheck.check_validation_health()
        print(json.dumps(health, indent=2))

        if health["overall"] == "healthy":
            print("\n✅ Validation system is healthy")
            return 0
        elif health["overall"] == "degraded":
            print("\n⚠️  Validation system is degraded")
            return 1
        else:
            print("\n❌ Validation system is unhealthy")
            return 2

    elif args.recent:
        # Show recent fallbacks
        logger = FallbackLogger()
        fallbacks = logger.get_recent_fallbacks(args.recent)

        if not fallbacks:
            print("No recent fallbacks")
            return 0

        print(f"\nRecent {len(fallbacks)} fallback(s):\n")
        for i, fb in enumerate(fallbacks, 1):
            print(f"{i}. {fb['timestamp']}")
            print(f"   Function: {fb['function']}")
            print(f"   Reason: {fb['reason']}")
            if fb['error']:
                print(f"   Error: {fb['error']}")
            print()

        return 0

    elif args.count:
        # Count fallbacks
        logger = FallbackLogger()
        count = logger.count_fallbacks_today()
        print(f"Fallbacks today: {count}")

        if count == 0:
            print("✅ No fallbacks - system is stable")
        elif count < 5:
            print("⚠️  Few fallbacks - monitor system")
        else:
            print("❌ Many fallbacks - investigation needed")

        return 0

    elif args.clear_logs:
        # Clear logs
        logger = FallbackLogger()
        for log_file in logger.log_dir.glob("fallback-*.log"):
            log_file.unlink()
        print("✅ Fallback logs cleared")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
