---
name: bt4g-xxx
description: Search for magnet links for specific XXX content using default keywords.
---

# BT4G XXX Magnet Search Skill

This skill allows you to search for magnet links on bt4gprx.com for specific adult content using a predefined set of keywords and logic.

## Usage

1.  **Trigger**: Use this skill when the user asks to "find xxx magnets", "get xxx links", or references the "xxx" variant of the magnet search.
2.  **Run the Script**:
    Execute the Python script located at `scripts/magnet_search_xxx.py`. No arguments are needed as it uses hardcoded keywords.
    
    ```bash
    python <path_to_skill>/scripts/magnet_search_xxx.py
    ```

    *Note: Replace `<path_to_skill>` with the absolute path to this skill's directory.*

3.  **Output**:
    The script will generate a file named `magnet_links_XXX.txt` in the **current working directory**.
    
    - Read the generated file to verify it contains links.
    - Inform the user that the links have been saved.

## Dependencies

The script requires:
- `DrissionPage`
- `Python 3`

Ensure these are installed (or run in the user's configured environment/venv).
