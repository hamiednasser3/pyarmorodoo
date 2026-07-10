# Pyarmor obfuscate your custom Odoo module


USAGE
-----
### BEFORE STARTING, YOU MUST MAKE A BACKUP OF YOUR CUSTOM MODULE BEFORE OBFUSCATE

1. Run on the CLIENT's Server first to get hardware id:

          # windows: use powershell cmd
          (Get-CimInstance Win32_Processor | Select-Object -First 1).ProcessorId
   
          # Linux (no admin user need):
          cat /etc/machine-id
   
          # Mac:
          ioreg -rd1 -c IOPlatformExpertDevice | awk -F'"' '/IOPlatformUUID/{print $4}'

3. Paste that value into _LICENSED_MACHINE_ID variable in license_check.py.
4. Drop license_check.py file into your module's root folder, next to __init__.py.
5. At the very top of that module's __init__.py -- before any other imports --
   add:

       from . import license_check
       license_check.verify_license()

6. Run the whole module folder through PyArmor as:

        "YOUR ODOO PYTHON ENV VERSION COMMAND" -m pyarmor.cli gen --recursive -i --output "absolute folder path for encryption output" "absolute folder path of your custom module"
   
7.  Copy with overwrite all generated content of encryption folder into the root folder of your custom module.
8.  Delete all __pycache__ folders inside your module.
9.  Restart odoo service.

   ***THAT'S ALL***

Notice:
Install pyarmor if not yet installed:

       pip install pyarmor


