# Encrypt your Odoo module in windows
## Windows Hardware-lock for a custom Odoo module.

USAGE
-----
### BEFORE STARTING, YOU MUST MAKE A BACKUP OF YOUR CUSTOM MODULE BEFORE ENCRYPTION

1. Run on the CLIENT's PC first to get cpu_id, use powershell cmd:

       (Get-CimInstance Win32_Processor | Select-Object -First 1).ProcessorId

2. Paste that value into _LICENSED_CPU_ID variable in license_check.py.
3. Drop license_check.py file into your module's root folder, next to __init__.py.
4. At the very top of that module's __init__.py -- before any other imports --
   add:

       from . import license_check
       license_check.verify_license()

5. Run the whole module folder through PyArmor as:

        "C:\Program Files\Odoo folder change it as yours\python\python.exe" -m pyarmor.cli gen --recursive -i --output "absolute folder path for encryption output" "absolute folder path of your custom module"
   
7.  Copy with overwrite all generated content of encryption folder into the root folder of your custom module.
8.  Delete all __pycache__ folders inside your module.
9.  Restart odoo service.

   ***THAT'S ALL***

Notice:
Install pyarmor if not yet installed:

       pip install pyarmor


