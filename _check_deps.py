try:
    from PIL import Image
    print("PIL OK")
except ImportError:
    print("PIL MISSING - installing...")
    import subprocess
    subprocess.run(["pip", "install", "Pillow"], check=True)
    from PIL import Image
    print("PIL installed OK")

import requests
print("requests OK")
import concurrent.futures
print("concurrent OK")
