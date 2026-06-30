try:
    from DrissionPage import ChromiumPage
    print("DrissionPage imported successfully")
    print("Version:", ChromiumPage.__module__)
except ImportError as e:
    print(f"Import error: {e}")
    import sys
    print("Python:", sys.executable)
    print("Path:", sys.path[:5])
