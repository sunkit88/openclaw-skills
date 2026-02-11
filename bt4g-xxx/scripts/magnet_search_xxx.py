import sys
import time
from DrissionPage import ChromiumPage

def handle_cloudflare(page, max_retries=3):
    """Check and handle Cloudflare turnstile/challenge with enhanced detection."""
    for attempt in range(max_retries):
        try:
            # Check for Cloudflare challenge
            title = page.title or ''
            if 'Just a moment' not in title and 'Cloudflare' not in title:
                # Extra content check
                try:
                    cf_check = page.ele('text:Checking your browser', timeout=1)
                    if not cf_check:
                        return True  # No challenge
                except:
                    return True
            
            print(f"Cloudflare challenge detected (attempt {attempt + 1}/{max_retries})...")
            
            time.sleep(2)
            
            # Method 1: Checkbox label
            challenge = page.ele('@class=ctp-checkbox-label', timeout=3)
            if challenge:
                print("Found checkbox label, clicking...")
                challenge.click()
                time.sleep(3)
                if 'Just a moment' not in (page.title or ''):
                    return True
                continue

            # Method 2: Iframe
            iframe = page.get_frame('@title^Widget containing a cloudflare')
            if iframe:
                print("Found Cloudflare iframe.")
                cb = iframe.ele('@type=checkbox', timeout=3) or iframe.ele('.mark', timeout=3)
                if cb:
                    print("Clicking verify checkbox in iframe...")
                    cb.click()
                    time.sleep(3)
                    if 'Just a moment' not in (page.title or ''):
                        return True
                    continue
            
            # Method 3: Turnstile checkbox
            turnstile = page.ele('css:input[type="checkbox"]', timeout=2)
            if turnstile:
                print("Found turnstile checkbox, clicking...")
                turnstile.click()
                time.sleep(3)
                if 'Just a moment' not in (page.title or ''):
                    return True
                continue
            
            # Method 4: Auto-resolve wait
            print("Waiting for Cloudflare to auto-resolve...")
            for _ in range(10):  # Wait up to 10s
                time.sleep(1)
                if 'Just a moment' not in (page.title or '') and 'Cloudflare' not in (page.title or ''):
                    print("Cloudflare challenge passed!")
                    return True
            
            # Manual fallback
            if attempt == max_retries - 1:
                print("⚠️ Please handle Cloudflare manually (waiting 15s)...")
                time.sleep(15)
                if 'Just a moment' not in (page.title or ''):
                    return True
                    
        except Exception as e:
            print(f"Cloudflare handling error: {e}")
            time.sleep(2)
    
    return False

def scrape_magnets():
    # Initialize ChromiumPage
    page = ChromiumPage()
    
    # Set 1 Keywords
    KEYWORDS_SET1_BASE = [
        "FamilyTherapyXXX", "metartx", "mysistershotfriend", "perfect18", "sexart", 
        "Tiny4K", "ImmoralLive", "tonightsgirlfriend", "sinful", "GirlsOutWest", 
        "OnlyTarts", "FrolicMe", "Watch4Beauty", "EvilAngel", "brattysis", 
        "CrazyCollegeGFs", "AllGirlMassage", "MommysGirl"
    ]
    KEYWORDS_SET1 = [f"{kw} XXX.1080p.HEVC.x265.PRT" for kw in KEYWORDS_SET1_BASE]
    
    # Set 2 Keywords
    KEYWORDS_SET2 = [
        "XXX.1080p.HEVC.x265.PRT",
        "XXX.1080p.MP4-WRB[XC]"
    ]
    
    all_magnet_links = set()
    set1_detail_urls = set()
    
    # ==================== Process Set 1 ====================
    for keyword in KEYWORDS_SET1:
        print(f"\n{'='*60}")
        print(f"[Set 1] Searching: {keyword} (Limit: First 5 results)")
        print(f"{'='*60}")
        
        url = f"https://bt4gprx.com/search?q={keyword}"
        
        print(f"Navigating to {url}...")
        page.get(url)
        
        handle_cloudflare(page)
        
        magnet_links = set()
        detail_urls = []
        
        # Collect first 5 detail page URLs
        links = page.eles('css:h5 a')
        count = 0
        for link in links:
            if count >= 5: break
            href = link.attr('href')
            if href:
                if not href.startswith('http'):
                    href = 'https://bt4gprx.com' + href
                detail_urls.append(href)
                set1_detail_urls.add(href)
                count += 1
        
        print(f"Found {len(detail_urls)} pages.")
        
        # Extract magnets
        for idx, detail_url in enumerate(detail_urls):
            print(f"Processing ({idx+1}/{len(detail_urls)}): {detail_url}")
            try:
                page.get(detail_url)
                handle_cloudflare(page)
                
                magnet_btn = page.ele('text:Magnet Link', timeout=2)
                
                if magnet_btn:
                    href = magnet_btn.attr('href')
                    if href and href.startswith('magnet:'):
                        print(f"Found direct magnet.")
                        magnet_links.add(href)
                    else:
                        magnet_btn.click()
                        if page.wait.new_tab(timeout=3):
                            tab = page.latest_tab
                            # New tab CF handling
                            def handle_new_tab_cloudflare(tab, max_wait=20):
                                for attempt in range(3):
                                    try:
                                        if 'Just a moment' not in (tab.title or ''): return True
                                        time.sleep(2)
                                        iframe = tab.get_frame('@title^Widget containing a cloudflare')
                                        if iframe:
                                            cb = iframe.ele('@type=checkbox', timeout=3)
                                            if cb: cb.click(); time.sleep(5)
                                        if 'Just a moment' not in (tab.title or ''): return True
                                    except: pass
                                return False
                            
                            handle_new_tab_cloudflare(tab)
                            
                            found_ele = tab.ele('css:input#magnetLink, input[value^="magnet:"], a[href^="magnet:"]', timeout=10)
                            mag = None
                            if found_ele:
                                if found_ele.tag == 'input': mag = found_ele.attr('value')
                                elif found_ele.tag == 'a': mag = found_ele.attr('href')
                            
                            if mag:
                                print(f"Found magnet.")
                                magnet_links.add(mag)
                            tab.close()
                        else:
                            mag_ele = page.ele('css:a[href^="magnet:"]', timeout=2)
                            if mag_ele: magnet_links.add(mag_ele.attr('href'))
            except Exception as e:
                print(f"Error: {e}")
        
        all_magnet_links.update(magnet_links)
    
    # ==================== Process Set 2 ====================
    for keyword in KEYWORDS_SET2:
        print(f"\n{'='*60}")
        print(f"[Set 2] Searching: {keyword} (Limit: First page max 15)")
        print(f"{'='*60}")
        
        url = f"https://bt4gprx.com/search?q={keyword}"
        page.get(url)
        handle_cloudflare(page)
        
        magnet_links = set()
        detail_urls = []
        
        links = page.eles('css:h5 a')
        count = 0
        skipped = 0
        for link in links:
            if count >= 15: break
            href = link.attr('href')
            if href:
                if not href.startswith('http'): href = 'https://bt4gprx.com' + href
                if href in set1_detail_urls:
                    skipped += 1
                    continue
                detail_urls.append(href)
                count += 1
        
        print(f"Found {len(detail_urls)} pages (skipped {skipped} dups).")
        
        for idx, detail_url in enumerate(detail_urls):
            print(f"Processing ({idx+1}/{len(detail_urls)}): {detail_url}")
            try:
                page.get(detail_url)
                handle_cloudflare(page)
                magnet_btn = page.ele('text:Magnet Link', timeout=2)
                if magnet_btn:
                    href = magnet_btn.attr('href')
                    if href and href.startswith('magnet:'):
                        magnet_links.add(href)
                    else:
                        magnet_btn.click()
                        if page.wait.new_tab(timeout=3):
                            tab = page.latest_tab
                            # Simplified tab CF handling for brevity as it mirrors above
                            time.sleep(2)
                            found_ele = tab.ele('css:input#magnetLink, input[value^="magnet:"], a[href^="magnet:"]', timeout=10)
                            mag = None
                            if found_ele:
                                if found_ele.tag == 'input': mag = found_ele.attr('value')
                                elif found_ele.tag == 'a': mag = found_ele.attr('href')
                            if mag: magnet_links.add(mag)
                            tab.close()
                        else:
                            mag_ele = page.ele('css:a[href^="magnet:"]', timeout=2)
                            if mag_ele: magnet_links.add(mag_ele.attr('href'))
            except Exception: pass
            
        all_magnet_links.update(magnet_links)

    # 3. Save to file
    output_file = 'magnet_links_XXX.txt'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for link in all_magnet_links:
                f.write(link + '\n')
        print(f"\nDone. Saved {len(all_magnet_links)} magnet links to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
    
    page.quit()

if __name__ == "__main__":
    scrape_magnets()
