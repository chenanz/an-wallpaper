try:
    import PIL
    print(f"PIL version: {PIL.__version__}")
    from PIL import Image
    print("PIL import OK")
except ImportError as e:
    print(f"PIL import FAILED: {e}")
