# Copyright (c) 2026 1abcdefggs
# Licensed under the MIT License
# See LICENSE file in the project root for full license information

#!/usr/bin/env python3
"""
Standalone TOC Generator for Google Colab
This script generates a table of contents for Colab notebooks without requiring external modules.

Background:
When working with AI assistants like Gemini in Colab, they often reference Cell IDs when explaining
code or content. This tool helps you map Cell IDs to their corresponding headings and content,
making it easier to understand which cell the AI is referring to.

Usage:
1. Copy this code to a new cell in your Colab notebook
2. Run the cell to generate a table of contents
3. Customize parameters in generate_standalone_toc() as needed:
   - filter_type: "All", "Code", or "Markdown"
   - keyword: Search keyword (empty string for all cells)
   - match_mode: "Cell-ID" or "Content"
   - limit: Preview character limit (default: 70)
   - show_jump: Show jump links (True/False)
   - show_stats: Show statistics (True/False)
   - save_log: Save to "TOC Preview.md" (True/False)

Source: https://github.com/1abcdefggs/cell-id-call
"""

import IPython
import json
import os
from google.colab import _message
from IPython.display import display, HTML

def _extract_heading_preview_standalone(source, cell_type, limit):
    """Extract heading preview from cell source."""
    text = "".join(source) if isinstance(source, list) else str(source)
    text = text.strip().replace("\n", " ")
    if cell_type == "markdown" and text.startswith("#"):
        cleaned = text.lstrip("#").strip()
        if not cleaned: return "(Empty heading)"
        return f"**{cleaned[:limit]}**" if len(cleaned) > limit else f"**{cleaned}**"
    return f"{text[:limit]}..." if len(text) > limit else text

def generate_standalone_toc(filter_type, keyword, match_mode, limit, show_jump, show_stats, save_log):
    """Generate standalone TOC for Colab notebook."""
    resp = _message.blocking_request('get_ipynb')
    if not resp or 'ipynb' not in resp: return
    cells = resp['ipynb'].get('cells', [])

    # Precise ID and Alignment Logic
    processed_ids = []
    for c in cells:
        meta = c.get('metadata', {})
        cid = meta.get('colab', {}).get('id') or c.get('id') or meta.get('id') or "unknown"
        processed_ids.append(str(cid))

    max_id_len = max([len(cid) for cid in processed_ids]) if processed_ids else 12

    # Dynamic Column Width Calculation
    jump_link_base = "[Jump](#scrollTo=)"
    w_jump = max(len("Jump Link"), max_id_len + len(jump_link_base))
    w_id = max(len("Cell ID"), max_id_len + 2)

    h_jump = f" {('Jump Link').ljust(w_jump)} |" if show_jump else ""
    s_jump = f" {(':---').ljust(w_jump, '-')} |" if show_jump else ""

    header = f"| Type | Index |{h_jump} {('Cell ID').ljust(w_id)} | Heading / Preview |"
    sep = f"| :--- | :--- |{s_jump} {(':---').ljust(w_id, '-')} | :--- |"

    md_table = ["# 🔍 TOC Preview. Quick Navigation (Standalone)", f"Mode: `{match_mode}`, Filter: `{filter_type}`", header, sep]
    stats = {'markdown': 0, 'code': 0, 'total': len(cells)}
    match_count = 0

    for idx, cell in enumerate(cells):
        c_type = cell.get('cell_type', 'unknown')
        stats[c_type] = stats.get(c_type, 0) + 1
        if filter_type == "Code" and c_type != 'code': continue
        if filter_type == "Markdown" and c_type != 'markdown': continue

        cell_id = processed_ids[idx]
        source_text = "".join(cell.get('source', []))

        if keyword:
            if match_mode == "Cell-ID":
                if keyword != cell_id: continue
            else:
                if keyword.lower() not in source_text.lower(): continue

        match_count += 1
        preview = _extract_heading_preview_standalone(source_text, c_type, limit)
        icon = "📝" if c_type == 'markdown' else "💻"

        row = f"| {icon} | {idx:03d} |"
        if show_jump:
            row += f" {f'[Jump](#scrollTo={cell_id})'.ljust(w_jump)} |"

        row += f" {f'`{cell_id}`'.ljust(w_id)} | {preview} |"
        md_table.append(row)

    full_md = "\n".join(md_table)

    if save_log:
        with open("TOC Preview.md", "w", encoding="utf-8") as f: f.write(full_md)

    if show_stats: print(f"📊 Total: {stats['total']} | Matches: {match_count}")

    # UI Button with improved JS for copying
    js_content = json.dumps(full_md)
    button_id = "copy_btn_standalone"
    html_btn = f'''
    <div style="margin: 15px 0;">
        <button id="{button_id}" style="background: #1a73e8; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
            📋 Copy TOC to Clipboard
        </button>
    </div>
    <script>
    (function() {{
        const btn = document.getElementById("{button_id}");
        if (!btn) return;
        btn.onclick = function() {{
            const text = {js_content};
            if (!navigator.clipboard) {{
               const textArea = document.createElement("textarea");
               textArea.value = text;
               document.body.appendChild(textArea);
               textArea.select();
               try {{ document.execCommand('copy'); }} catch (err) {{ }}
               document.body.removeChild(textArea);
            }} else {{
                navigator.clipboard.writeText(text).then(() {{
                    const original = btn.innerText;
                    btn.innerText = "✅ Copied!";
                    btn.style.background = "#34a853";
                    setTimeout(() => {{
                        btn.innerText = original;
                        btn.style.background = "#1a73e8";
                    }}, 2000);
                }});
            }}
        }};
    }})();
    </script>
    '''
    display(HTML(html_btn))
    print("\n" + full_md)

# Default configuration for standalone execution
if __name__ == "__main__":
    generate_standalone_toc(
        filter_type="All",
        keyword="",
        match_mode="Cell-ID",
        limit=70,
        show_jump=True,
        show_stats=True,
        save_log=True
    )
