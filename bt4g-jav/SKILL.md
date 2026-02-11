---
name: bt4g-jav
description: Search and download JAV magnet links from bt4gprx.com. Accepts one or more JAV IDs (e.g., "SONE-123", "PRED-456"). Automatically tries "-c" suffix first, then falls back to original keyword.
---

# BT4G JAV Magnet Search Skill

This skill searches for JAV magnet links on bt4gprx.com using DrissionPage to handle Cloudflare protection.

## Usage

1. **Identify Keywords**: Extract JAV IDs from user request (e.g., "SONE-123", "PRED-456")
   - Keywords should be in format like `ABC-123` or `ABC123`
   - **If no keywords provided, ASK the user for keywords**

2. **Run the Script**:
   ```bash
   python <path_to_skill>/scripts/jav_magnet_search.py "keyword1" "keyword2" "keyword3"
   ```

   Example:
   ```bash
   python C:\Users\sunki\.gemini\antigravity\skills\bt4g-jav\scripts\jav_magnet_search.py "SONE-123" "PRED-456" "MIDA-789"
   ```

3. **Output**:
   - Results are saved to `jav_magnet_links.txt` in the **current working directory**
   - Each line contains: `keyword: magnet_link`
   - Script prints progress and results to stdout

## Search Logic

For each keyword, the script:
1. First searches with `-c` suffix (e.g., `SONE-123-c`)
2. If no results, falls back to original keyword (e.g., `SONE-123`)
3. Filters results by looking for:
   - Priority 1: Files containing `最新位址獲取.txt`
   - Priority 2: Files containing `hhd800.com@`
4. Extracts the magnet link from the detail page

## Dependencies

- `DrissionPage` (handles Chromium browser automation)
- `Python 3`

Ensure DrissionPage is installed or run in the user's configured venv.
