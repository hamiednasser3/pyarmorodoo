# -*- coding: utf-8 -*-
"""
Hardware-lock check for a custom Odoo module.

USAGE
-----
1. Run get_cpu_id.py on the CLIENT's PC first, to find the value to use below.
2. Paste that value into _LICENSED_CPU_ID.
3. Drop this file into your module's root folder, next to __init__.py.
4. At the very top of that module's __init__.py -- before any other imports --
   add:

       from . import license_check
       license_check.verify_license()

5. Run the whole module folder through PyArmor as normal. This file MUST be
   obfuscated along with everything else. If you leave it in plain text,
   anyone can open it and delete the check -- it only has teeth once it's
   inside the obfuscated bundle.
"""

import logging
import subprocess

_logger = logging.getLogger(__name__)

# Replace with the client machine's actual CPU ID (see get_cpu_id.py).
_LICENSED_CPU_ID = "cpu_id"


def _read_cpu_id():
    """Read this machine's CPU identifier via WMI. Windows only."""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_Processor | Select-Object -First 1).ProcessorId",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception as exc:
        _logger.critical("Could not read CPU id: %s", exc)
        return ""


def _read_disk_serial():
    """
    OPTIONAL extra check. Windows' reported CPU id is derived from the
    CPU model/stepping, not a true per-chip serial -- two PCs with the
    identical CPU model can report the same value. If you want a more
    solid per-machine fingerprint, combine this with the CPU id (call
    it from verify_license() and require both to match).
    """
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_DiskDrive | Select-Object -First 1).SerialNumber",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception as exc:
        _logger.critical("Could not read disk serial: %s", exc)
        return ""


def verify_license():
    """
    Raise if this machine's CPU id doesn't match the licensed one.
    Call this at the very top of __init__.py, before importing models,
    so a failed check stops the module from registering anything.
    """
    current_id = _read_cpu_id()
    if not current_id or current_id != _LICENSED_CPU_ID:
        _logger.critical(
            "Module license check failed -- this machine is not authorized "
            "to run this module."
        )
        raise RuntimeError("This module is not licensed for this machine.")
    _logger.info("Module license check passed.")
