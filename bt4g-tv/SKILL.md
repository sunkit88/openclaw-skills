---
name: bt4g-tv
description: Search for and generate magnet links for a given keyword from bt4gprx.com. Use this skill when the user asks to "find magnets", "get magnet links", or reference "bt4g" for a specific show or term.
---

# BT4G Magnet Search Skill

This skill allows you to search for magnet links on bt4gprx.com using a Python script that handles Cloudflare protection.

## Usage

1.  **Identify the Keyword**: Extract the search term from the user's request.
    - If the user provides a keyword (e.g., "find magnet for Inception"), use "Inception".
    - **Crucial**: If no keyword is provided, **you MUST ask the user for a keyword** before proceeding.

2.  **Run the Script**:
    Execute the Python script located at `scripts/magnet_search.py` with the keyword as an argument.
    
    ```bash
    python <path_to_skill>/scripts/magnet_search.py "<keyword>"
    ```

    *Note: Replace `<path_to_skill>` with the absolute path to this skill's directory.*

3.  **Output**:
    The script will generate a file named `magnet_links.txt` (or similar, check script output) in the **current working directory**.
    
    - Read the generated file to verify it contains links.
    - Inform the user that the links have been saved.

## Dependencies

The script requires:
- `DrissionPage`
- `Python 3`

Ensure these are installed (or run in the user's configured environment/venv).
