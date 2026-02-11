#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
jav_magnet_search.py - Search and extract JAV magnet links from bt4gprx.com
Usage: python jav_magnet_search.py "keyword1" "keyword2" ...
"""

import sys
import os

# 設置標準輸出編碼為UTF-8，並開啟行緩衝以實現實時輸出
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from DrissionPage import ChromiumPage
from DrissionPage.errors import PageDisconnectedError

# --- Configuration ---
BASE_URL = "https://bt4gprx.com"
OUTPUT_FILE = "jav_magnet_links.txt"


def handle_cloudflare(page):
    """檢查並處理 Cloudflare 挑戰"""
    try:
        if 'Just a moment' in page.title or 'Cloudflare' in page.title:
            print("偵測到 Cloudflare 挑戰...")
            
            # 嘗試喺 iframe 入面搵 checkbox
            iframe = page.get_frame('@title^Widget containing a cloudflare')
            if iframe:
                cb = iframe.ele('@type=checkbox', timeout=2) or iframe.ele('.mark', timeout=2)
                if cb:
                    print("找到驗證 Checkbox，嘗試點擊...")
                    cb.click()
                    page.wait.url_change(page.url, timeout=10)
                    return True
            
            # 如果搵唔到 checkbox，等 redirect
            print("等待 Cloudflare 自動跳轉...")
            page.wait.url_change(page.url, timeout=15)
    except Exception as e:
        print(f"處理 Cloudflare 時發生錯誤：{e}")


def parse_size_to_bytes(size_str):
    """將檔案大小字串轉換為 bytes 數值，用於比較"""
    try:
        size_str = size_str.upper().strip()
        if 'GB' in size_str:
            return float(size_str.replace('GB', '').strip()) * 1024 * 1024 * 1024
        elif 'MB' in size_str:
            return float(size_str.replace('MB', '').strip()) * 1024 * 1024
        elif 'KB' in size_str:
            return float(size_str.replace('KB', '').strip()) * 1024
        elif 'B' in size_str:
            return float(size_str.replace('B', '').strip())
    except:
        pass
    return float('inf')  # 無法解析就排最後


def check_result_match(page, keyword):
    """
    檢查搜尋結果嘅檔案列表是否包含特定標記
    優先級：
    1. 包含 "最新位址獲取.txt"（排除 4K 版本，選最細 size）
    2. 包含 "hhd800.com@"（排除 4K 版本，選最細 size）
    如果都無，即使有結果都視為無效
    返回匹配嘅結果項目嘅詳情頁 URL，無匹配返回 None
    """
    # 使用 timeout=2 加快無結果偵測
    result_items = page.eles('css:div.list-group-item.result-item', timeout=2)
    
    if not result_items:
        print(f"  ❌ 無搜尋結果")
        return None
    
    print(f"  📜 找到 {len(result_items)} 個結果，開始過濾...")
    
    def collect_matches(marker):
        """收集所有匹配指定標記嘅結果"""
        matches = []
        for idx, item in enumerate(result_items):
            try:
                # 檢查標題是否包含 4K
                title_ele = item.ele('css:h5 a')
                if title_ele:
                    title_text = title_ele.text.upper()
                    if '4K' in title_text:
                        continue  # 跳過 4K 版本
                
                ul = item.ele('tag:ul')
                if ul:
                    ul_text = ul.text
                    ul_text_nospace = ul_text.replace(" ", "")
                    
                    if marker in ul_text_nospace:
                        # 提取 size（從 result-item 嘅 metadata）
                        size_ele = item.ele('css:span.cpill:nth-child(3)', timeout=0.5)
                        size_str = size_ele.text if size_ele else "999GB"
                        size_bytes = parse_size_to_bytes(size_str)
                        
                        link = item.ele('css:h5 a')
                        if link:
                            href = link.attr('href')
                            if href and "/magnet/" in href:
                                if not href.startswith('http'):
                                    href = BASE_URL + href
                                matches.append({
                                    'idx': idx + 1,
                                    'href': href,
                                    'size_str': size_str,
                                    'size_bytes': size_bytes
                                })
            except Exception as e:
                print(f"  ⚠️ 處理第 {idx+1} 項時出錯：{e}")
        return matches
    
    # 第一輪：搵包含 "最新位址獲取.txt" 嘅結果
    matches = collect_matches("最新位址獲取.txt")
    if matches:
        # 選最細 size
        best = min(matches, key=lambda x: x['size_bytes'])
        print(f"  ✓ 找到 {len(matches)} 個匹配（最新位址獲取.txt），選擇第 {best['idx']} 項（{best['size_str']}）")
        return best['href']
    
    # 第二輪：搵包含 "hhd800.com@" 嘅結果
    matches = collect_matches("hhd800.com@")
    if matches:
        best = min(matches, key=lambda x: x['size_bytes'])
        print(f"  ✓ 找到 {len(matches)} 個匹配（hhd800.com@），選擇第 {best['idx']} 項（{best['size_str']}）")
        return best['href']
    
    print(f"  ❌ 無匹配嘅結果（有結果但不符合標記要求）")
    return None


def extract_magnet_from_detail(page, detail_url):
    """從詳情頁提取磁力連結"""
    try:
        page.get(detail_url)
        handle_cloudflare(page)
        
        # 搵 Magnet Link 按鈕
        magnet_btn = page.ele('text:Magnet Link', timeout=5)
        
        if magnet_btn:
            href = magnet_btn.attr('href')
            
            if href and href.startswith('magnet:'):
                return href
            else:
                # 點擊按鈕可能會開新 tab
                magnet_btn.click()
                if page.wait.new_tab(timeout=3):
                    tab = page.latest_tab
                    try:
                        # 處理新 tab 嘅 Cloudflare
                        if 'Just a moment' in tab.title:
                            iframe = tab.get_frame('@title^Widget containing a cloudflare')
                            if iframe:
                                cb = iframe.ele('@type=checkbox', timeout=2)
                                if cb:
                                    cb.click()
                                    tab.wait.url_change(tab.url, timeout=5)
                        
                        # 搵磁力連結
                        found_ele = tab.ele('css:input#magnetLink, input[value^="magnet:"], a[href^="magnet:"]', timeout=10)
                        
                        if found_ele:
                            if found_ele.tag == 'input':
                                return found_ele.attr('value')
                            elif found_ele.tag == 'a':
                                return found_ele.attr('href')
                    finally:
                        tab.close()
                else:
                    # 無新 tab，喺當前頁面搵
                    mag_link_ele = page.ele('css:a[href^="magnet:"]', timeout=2)
                    if mag_link_ele:
                        return mag_link_ele.attr('href')
    except Exception as e:
        print(f"  ⚠️ 提取磁力連結時出錯：{e}")
    
    return None


def search_and_extract(page, keyword):
    """搜尋單個 keyword 並提取磁力連結"""
    # 嘗試 keyword-c 格式
    search_keyword = f"{keyword}-c"
    search_url = f"{BASE_URL}/search?q={search_keyword}&orderby=size"
    
    print(f"\n🔍 搜尋 '{search_keyword}'...")
    page.get(search_url)
    handle_cloudflare(page)
    
    # 檢查結果
    detail_url = check_result_match(page, keyword)
    
    # 如果 -c 格式無結果，嘗試原始 keyword
    if not detail_url:
        print(f"  ⏭️ 嘗試原始 keyword '{keyword}'...")
        search_url = f"{BASE_URL}/search?q={keyword}&orderby=size"
        page.get(search_url)
        handle_cloudflare(page)
        detail_url = check_result_match(page, keyword)
    
    if detail_url:
        print(f"  📥 進入詳情頁：{detail_url}")
        magnet = extract_magnet_from_detail(page, detail_url)
        if magnet:
            return magnet
    
    return None


def main(keywords):
    """主執行函數"""
    print("=" * 60)
    print("🚀 BT4G JAV Magnet Search")
    print(f"🎯 搜尋 {len(keywords)} 個關鍵字")
    print("=" * 60)
    
    # 初始化瀏覽器
    print("\n🌐 初始化 ChromiumPage...")
    page = ChromiumPage()
    
    results = {}
    
    for i, keyword in enumerate(keywords, 1):
        keyword = keyword.strip().upper()
        if not keyword:
            continue
            
        try:
            print(f"\n[{i}/{len(keywords)}] 處理 '{keyword}'")
            
            magnet = search_and_extract(page, keyword)
            
            if magnet:
                print(f"  ✅ 成功獲取磁力連結")
                results[keyword] = magnet
            else:
                print(f"  ❌ 無法獲取磁力連結")
                results[keyword] = None
                
        except PageDisconnectedError:
            print(f"  ⚠️ 頁面斷開連線，重新初始化瀏覽器...")
            try:
                page.quit()
            except:
                pass
            page = ChromiumPage()
            # 重試當前 keyword
            try:
                magnet = search_and_extract(page, keyword)
                if magnet:
                    print(f"  ✅ 重試成功")
                    results[keyword] = magnet
                else:
                    results[keyword] = None
            except:
                results[keyword] = None
        except Exception as e:
            print(f"  ⚠️ 處理時發生錯誤：{e}")
            results[keyword] = None
    
    try:
        page.quit()
    except:
        pass
    
    # 寫入結果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for keyword, magnet in results.items():
            if magnet:
                f.write(f"{keyword}: {magnet}\n")
            else:
                f.write(f"{keyword}: NOT_FOUND\n")
    
    # 統計
    success_count = sum(1 for m in results.values() if m)
    
    print("\n" + "=" * 60)
    print(f"🎉 完成！成功獲取 {success_count}/{len(results)} 個磁力連結")
    print(f"📄 結果已保存至 {OUTPUT_FILE}")
    print("=" * 60)
    
    # 列出結果
    print("\n📋 結果摘要：")
    for keyword, magnet in results.items():
        if magnet:
            print(f"  ✓ {keyword}")
        else:
            print(f"  ✗ {keyword}")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python jav_magnet_search.py \"keyword1\" \"keyword2\" ...")
        print("Example: python jav_magnet_search.py \"SONE-123\" \"PRED-456\"")
        sys.exit(1)
    
    keywords = sys.argv[1:]
    main(keywords)
