import sys
import argparse
import time
from DrissionPage import ChromiumPage

def handle_cloudflare(page):
    """Check and handle Cloudflare turnstile/challenge."""
    try:
        if 'Just a moment' in page.title or 'Cloudflare' in page.title:
            print("Cloudflare challenge detected.")
            
            # Method 1: Try finding the challenge frame and clicking properties
            challenge = page.ele('@class=ctp-checkbox-label', timeout=2)
            if challenge:
                print("Found checkbox label, clicking...")
                challenge.click()
                page.wait.url_change(timeout=10, exclude_url=True)
                return True

            # Method 2: Generic iframe/shadow search for checkbox
            iframe = page.get_frame('@title^Widget containing a cloudflare')
            if iframe:
                print("Found Cloudflare iframe.")
                cb = iframe.ele('@type=checkbox', timeout=2) or iframe.ele('.mark', timeout=2)
                if cb:
                    print("Clicking verify checkbox in iframe...")
                    cb.click()
                    page.wait.url_change(timeout=10, exclude_url=True)
                    return True
            
            print("Cloudflare check found but no button. Waiting for redirect...")
            page.wait.url_change(timeout=10, exclude_url=True)
    except Exception as e:
        pass

def scrape_magnets(keyword):
    print(f"Initializing ChromiumPage for keyword: {keyword}")
    page = ChromiumPage()
    
    all_magnet_links = set()
    
    print(f"\n{'='*60}")
    print(f"Starting search for: {keyword}")
    print(f"{'='*60}")
    
    url = f"https://bt4gprx.com/search?q={keyword}"
    
    print(f"Navigating to {url}...")
    page.get(url)
    
    handle_cloudflare(page)
    
    magnet_links = set()
    detail_urls = []
    seen_urls_global = set()

    # 1. Collect all detail page URLs across pagination
    page_num = 1
    while True:
        print(f"Collecting results from page {page_num}...")
        
        links = page.eles('css:h5 a')
        
        new_links_on_page = 0
        for link in links:
            href = link.attr('href')
            if href:
                if not href.startswith('http'):
                    href = 'https://bt4gprx.com' + href
                
                if href in seen_urls_global:
                    continue
                
                seen_urls_global.add(href)
                detail_urls.append(href)
                new_links_on_page += 1
        
        print(f"Found {new_links_on_page} new links on this page.")
        
        if new_links_on_page == 0:
            print("No new links found. Stopping pagination.")
            break

        # Check pagination
        next_btn = page.ele('css:ul.pagination li.page-item:last-child a')
        
        should_next = False
        if next_btn:
            parent_li = page.ele('css:ul.pagination li.page-item:last-child')
            item_class = parent_li.attr('class') or ''
            href = next_btn.attr('href')
            
            if href and 'disabled' not in item_class and href != '#' and href != page.url:
                should_next = True
                print("Going to next page...")
                next_btn.click()
                
                try:
                    page.wait.doc_loaded()
                    page.wait.ele_displayed('css:h5 a', timeout=5)
                except Exception:
                    pass
                    
                handle_cloudflare(page)
                page_num += 1
            else:
                print(f"Next button invalid or disabled")
        
        if not should_next:
            print("Pagination finished.")
            break

    print(f"Total unique detail pages found: {len(detail_urls)}")
    
    # 2. Extract magnet links
    for idx, detail_url in enumerate(detail_urls):
        print(f"Processing ({idx+1}/{len(detail_urls)}): {detail_url}")
        try:
            page.get(detail_url)
            handle_cloudflare(page)
            
            magnet_btn = page.ele('text:Magnet Link', timeout=2)
            
            if magnet_btn:
                href = magnet_btn.attr('href')
                
                if href and href.startswith('magnet:'):
                    print(f"Found direct magnet link.")
                    magnet_links.add(href)
                else:
                    magnet_btn.click()
                    if page.wait.new_tab(timeout=3):
                        tab = page.latest_tab
                        try:
                            # Handle CF on new tab
                            if 'Just a moment' in tab.title:
                                iframe = tab.get_frame('@title^Widget containing a cloudflare')
                                if iframe:
                                    cb = iframe.ele('@type=checkbox', timeout=2)
                                    if cb:
                                        cb.click()
                                        tab.wait.url_change(timeout=5, exclude_url=True)
                        except:
                            pass

                        found_ele = tab.ele('css:input#magnetLink, input[value^="magnet:"], a[href^="magnet:"]', timeout=10)
                        
                        mag = None
                        if found_ele:
                            if found_ele.tag == 'input':
                                mag = found_ele.attr('value')
                            elif found_ele.tag == 'a':
                                mag = found_ele.attr('href')
                            
                        if mag:
                            print(f"Found magnet.")
                            magnet_links.add(mag)
                        else:
                            print(f"Could not find magnet link on tab.")
                        
                        tab.close()
                    else:
                        mag_link_ele = page.ele('css:a[href^="magnet:"]', timeout=2)
                        if mag_link_ele:
                            magnet_links.add(mag_link_ele.attr('href'))
            else:
                print("Magnet Link button not found.")
                
        except Exception as e:
            print(f"Error processing {detail_url}: {e}")
    
    all_magnet_links.update(magnet_links)

    # 3. Save to file
    output_file = 'magnet_links.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for link in all_magnet_links:
            f.write(link + '\n')
            
    print(f"Done. Saved {len(all_magnet_links)} magnet links to {output_file}")
    
    page.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape magnet links from bt4gprx.com')
    parser.add_argument('keyword', help='Search keyword')
    args = parser.parse_args()
    
    scrape_magnets(args.keyword)
