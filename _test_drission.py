from DrissionPage import ChromiumPage, ChromiumOptions
import time

# Test if DrissionPage can access Lofter
try:
    # Try headless mode
    co = ChromiumOptions()
    co.headless()
    # co.set_argument('--no-sandbox')
    # co.set_argument('--disable-gpu')
    
    page = ChromiumPage(co)
    page.get("https://www.lofter.com/tag/原神同人?type=new")
    time.sleep(5)  # Wait for SPA to render
    
    # Get the page content after JS rendering
    html = page.html
    print(f"Page length: {len(html)}")
    
    # Look for images
    import re
    imgs = re.findall(r'(https?://[a-z0-9._:/-]+\.(?:jpg|png|jpeg|webp)(?:\?[^\s"\')]*)?)', html, re.IGNORECASE)
    print(f"Images found: {len(imgs)}")
    for img in imgs[:5]:
        print(f"  {img}")
    
    # Also check for post cards
    cards = page.eles('.post-card') or page.eles('.m-icard') or page.eles('[class*=post]')
    print(f"Post cards: {len(cards)}")
    
    page.quit()
except Exception as e:
    print(f"Error: {e}")
    # If headless fails, try with display
    try:
        page = ChromiumPage()
        page.get("https://www.lofter.com/tag/原神同人?type=new")
        time.sleep(8)
        html = page.html
        print(f"Display mode page length: {len(html)}")
        import re
        imgs = re.findall(r'(https?://[a-z0-9._:/-]+\.(?:jpg|png|jpeg|webp)(?:\?[^\s"\')]*)?)', html, re.IGNORECASE)
        print(f"Images found: {len(imgs)}")
        for img in imgs[:5]:
            print(f"  {img}")
        page.quit()
    except Exception as e2:
        print(f"Display mode also failed: {e2}")

