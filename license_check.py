# -*- coding: utf-8 -*-
"""
Cross-platform hardware-lock check for a custom Odoo module.

Works on Windows, Linux, and macOS.

USAGE
-----
1. Run this file's `python license_check.py --print-id` on the CLIENT's
   machine (or server) to find the value to use below.
2. Paste that value into _LICENSED_MACHINE_ID.
3. Drop this file into your module's root folder, next to __init__.py.
4. At the very top of that module's __init__.py -- before any other
   imports -- add:

       from . import license_check
       license_check.verify_license()

5. Run the whole module folder through PyArmor as normal. This file MUST
   be obfuscated along with everything else. If you leave it in plain
   text, anyone can open it and delete the check -- it only has teeth
   once it's inside the obfuscated bundle.

IMPORTANT CAVEATS (read before relying on this)
------------------------------------------------
- Docker: if Odoo runs in a container, the ID below is the CONTAINER's
  id/uuid, not the host's, unless you bind-mount the relevant file/path
  from the host. Containers are usually rebuilt on every deploy, which
  will break the lock unless you persist or mount the identifier.
- Multi-worker / load-balanced hosting (e.g. Odoo.sh-style setups) may
  present different machine IDs per worker/node.
- VM cloning: a cloned VM can carry over the same machine id on some
  platforms -- this check identifies a machine, it does not prove the
  license hasn't been copied onto a clone. For stronger anti-cloning,
  combine multiple IDs (see _read_disk_serial for an optional second
  factor) or move to a server-side phone-home license check.
- Anyone with sufficient access to a client's box can still eventually
  patch obfuscated bytecode or intercept subprocess calls. This is a
  deterrent for casual copying, not a cryptographically strong DRM
  system.
"""

import logging
import platform
import subprocess
import sys

_logger = logging.getLogger(__name__)

# Replace with the client machine's actual ID (see --print-id below).
_LICENSED_MACHINE_ID = "machine_id"


def _run(cmd, timeout=5):
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception as exc:
        _logger.critical("Command failed (%s): %s", cmd, exc)
        return ""


def _read_machine_id():
    """
    Return a per-machine identifier appropriate to the current OS.
    Empty string on failure (never raises).
    """
    system = platform.system()

    try:
        if system == "Windows":
            return _run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_Processor | "
                    "Select-Object -First 1).ProcessorId",
                ]
            )

        elif system == "Linux":
            # systemd machine-id: unique per install, no root, no subprocess.
            for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
                try:
                    with open(path) as f:
                        value = f.read().strip()
                        if value:
                            return value
                except FileNotFoundError:
                    continue
            return ""

        elif system == "Darwin":
            output = _run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"]
            )
            for line in output.splitlines():
                if "IOPlatformUUID" in line:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        return parts[-2]
            return ""

        else:
            _logger.critical("Unsupported platform: %s", system)
            return ""

    except Exception as exc:
        _logger.critical("Could not read machine id: %s", exc)
        return ""


def _read_disk_serial():
    """
    OPTIONAL second factor. A machine id alone can sometimes survive
    VM cloning; pairing it with a disk/volume serial gives modest extra
    resistance. Call this from verify_license() and require both to
    match if you want it. Not enabled by default.
    """
    system = platform.system()
    try:
        if system == "Windows":
            return _run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_DiskDrive | "
                    "Select-Object -First 1).SerialNumber",
                ]
            )
        elif system == "Linux":
            return _run(["lsblk", "-no", "SERIAL"]).splitlines()[0] if _run(
                ["lsblk", "-no", "SERIAL"]
            ) else ""
        elif system == "Darwin":
            output = _run(["diskutil", "info", "/"])
            for line in output.splitlines():
                if "Volume UUID" in line:
                    return line.split(":")[-1].strip()
            return ""
        else:
            return ""
    except Exception as exc:
        _logger.critical("Could not read disk serial: %s", exc)
        return ""


def verify_license():
    """
    Raise if this machine's id doesn't match the licensed one.
    Call this at the very top of __init__.py, before importing models,
    so a failed check stops the module from registering anything.
    """
    current_id = _read_machine_id()
    if not current_id or current_id != _LICENSED_MACHINE_ID:
        _logger.critical(
            "Module license check failed -- this machine is not authorized "
            "to run this module."
        )
        raise RuntimeError("This module is not licensed for this machine.")
    _logger.info("Module license check passed.")


if __name__ == "__main__":
    # Helper for step 1: run this directly on the target machine to get
    # the value to paste into _LICENSED_MACHINE_ID.
    #   python license_check.py --print-id
    if "--print-id" in sys.argv:
        mid = _read_machine_id()
        print("Machine ID:", mid or "(could not determine)")
        disk = _read_disk_serial()
        print("Disk serial (optional 2nd factor):", disk or "(could not determine)")
    else:
        print("Usage: python license_check.py --print-id")
