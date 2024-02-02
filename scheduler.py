import os
import subprocess

def execute_delete_expired_items():
    script_path = os.path.join(os.getcwd(), 'delete_expired_items.py')
    subprocess.call(['python', script_path])