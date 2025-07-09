"""Logger module."""

import sys
import json
import logging
from typing import Optional, Dict, Any

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from common.config import LOG_LEVEL, LOG_USE_BASIC_FORMAT, ENABLE_CLOUD_LOGGING


def setup_loggers(
    log_level: str = LOG_LEVEL,
    use_basic_format: bool = LOG_USE_BASIC_FORMAT,
    enable_google_cloud: bool = ENABLE_CLOUD_LOGGING,
    service_name: Optional[str] = None,
    service_version: Optional[str] = "1.0.0",
) -> None:
    """
    Configure loggers with the specified format and level.

    Args:
        log_level: Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        use_basic_format: If True, use basic text format. If False, use JSON format.
        enable_google_cloud: If True, enable Google Cloud Logging integration
        service_name: Name of the service for logging identification
        service_version: Version of the service for logging identification
    """
    # Remove default handler
    logger.remove()

    if use_basic_format:
        # Basic text format
        format_str = " | ".join(
            [
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>",
                "<level>{level: <8}</level>",
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>",
                "<level>{message}</level>",
            ]
        )
    else:
        # Structured JSON format
        def format_record(record) -> str:
            # Create a copy of extra to avoid modifying the original
            extra = dict(record.get("extra", {}))
            extra["service"] = service_name or "app"
            extra["version"] = service_version

            # Prepare the log record
            log_record = {
                "time": record["time"].isoformat(),
                "severity": record["level"].name,
                "message": record["message"],
                "service": service_name or "app",
                "version": service_version,
                "logger": record["name"],
                "function": record["function"],
                "line": record["line"],
                "extra": extra,
            }

            # Handle exceptions if present
            if record.get("exception"):
                exc = record["exception"]
                exc_info = {
                    "type": str(getattr(exc, "type", type(exc).__name__)),
                    "value": str(getattr(exc, "value", exc)),
                }
                # Only add traceback if it exists
                if hasattr(exc, "traceback") and exc.traceback is not None:
                    exc_info["traceback"] = exc.traceback.format_exc()
                log_record["exception"] = exc_info

            return json.dumps(log_record, default=str)

    # Configure console handler
    if use_basic_format:
        # For basic format, use the format string directly
        logger.add(
            sys.stderr,
            level=log_level.upper(),
            format=format_str,
            backtrace=True,
            diagnose=True,
            enqueue=True,  # Recommended for async applications
        )
        logger.info("Using basic logging format")
    else:
        # For JSON format, use a custom format function
        def make_json_sink(format_func):
            def json_sink(message):
                record = message.record
                try:
                    print(format_func(record), file=sys.stderr, flush=True)
                except Exception as e:
                    print(f"Error in JSON logging: {e}", file=sys.stderr)

            return json_sink

        # Create a sink with access to the format_record function
        sink = make_json_sink(format_record)

        logger.add(
            sink,
            level=log_level.upper(),
            format="{message}",  # This will be replaced by our custom sink
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )
        logger.info("Using structured logging format")

    # Google Cloud Logging integration if enabled
    if enable_google_cloud:
        try:
            import google.cloud.logging
            from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging

            def cloud_logging_sink(message):
                record = message.record
                # Map Loguru levels to Cloud Logging severity
                level_no = record["level"].no
                level_name = record["level"].name

                # Map Loguru levels to Cloud Logging severity
                if level_no >= 50:  # CRITICAL
                    severity = "CRITICAL"
                elif level_no >= 40:  # ERROR
                    severity = "ERROR"
                elif level_no >= 30:  # WARNING
                    severity = "WARNING"
                elif level_name == "SUCCESS":  # Special case for SUCCESS level (25)
                    severity = "NOTICE"  # Or 'INFO' if you prefer
                elif level_no >= 20:  # INFO
                    severity = "INFO"
                elif level_no >= 10:  # DEBUG
                    severity = "DEBUG"
                else:  # TRACE or custom levels below DEBUG
                    severity = "DEBUG"  # Or 'DEFAULT' if you prefer

                # Prepare the log entry
                log_entry = {
                    "severity": severity,
                    "message": record["message"],
                    "serviceContext": {
                        "service": service_name or "app",
                        "version": service_version,
                    },
                    "logging.googleapis.com/sourceLocation": {
                        "file": record["file"].name,
                        "line": record["line"],
                        "function": record["function"],
                    },
                    "labels": {"logger": record["name"], "level": record["level"].name},
                }

                # Add exception info if present
                if record.get("exception"):
                    exc = record["exception"]
                    exc_info = {
                        "type": str(getattr(exc, "type", type(exc).__name__)),
                        "value": str(getattr(exc, "value", exc)),
                    }

                    # Safely get traceback if it exists
                    if hasattr(exc, "traceback"):
                        try:
                            exc_info["traceback"] = exc.traceback.format()
                        except Exception:
                            exc_info["traceback"] = "Error formatting traceback"

                    log_entry["exception"] = exc_info

                # Add any extra context
                extra = {
                    k: v for k, v in record["extra"].items() if not k.startswith("__")
                }
                if extra:
                    log_entry["extra"] = extra

                # Get the Cloud Logging client and logger
                client = google.cloud.logging.Client()
                logger_cloud = client.logger(service_name or "app")

                # Log the entry with the appropriate severity
                logger_cloud.log_struct(log_entry, severity=severity)

            # Add the Cloud Logging sink
            logger.add(
                cloud_logging_sink,
                level=log_level.upper(),
                format=LOGURU_FORMAT,
                enqueue=True,
                catch=True,
            )

            logger.info("Google Cloud Logging has been successfully configured")
        except ImportError:
            logger.warning(
                "Google Cloud Logging client is not installed. "
                "Install with: pip install google-cloud-logging"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Logging: {str(e)}")

    # Set the log level for all loggers
    logger.level(log_level.upper())
    logger.info(f"Logging configured with level: {log_level}")
