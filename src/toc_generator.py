import hashlib
import os
import IPython
import json
from google.colab import _message
from IPython.display import display, HTML

def _get_notebook_cells():
    resp = _message.blocking_request("get_ipynb")
    if not resp or "ipynb" not in resp:
        print("Failed to get notebook structure.")
        return None
    return resp["ipynb"].get("cells", [])

def _extract_heading_preview(source, cell_type, limit):
    text = "".join(source) if isinstance(source, list) else str(source)
    text = text.strip().replace("\n", " ")
    if cell_type == "markdown" and text.startswith("#"):
        cleaned = text.lstrip("#").strip()
        if not cleaned: return "(Empty heading)"
        return f"**{cleaned[:limit]}**" if len(cleaned) > limit else f"**{cleaned}**"
    return f"{text[:limit]}..." if len(text) > limit else text

def set_toc_len(new_len):
    ip = IPython.get_ipython()
    ip.db["colab_toc_max_len"] = int(new_len)
    print(f"Display length set to {new_len}.")

def generate_advanced_toc(filter_type="All", keyword="", show_stats=True, strict_id_match=False, show_jump_links=True, save_log=False):
    ip = IPython.get_ipython()
    stored_limit = ip.db.get("colab_toc_max_len", 30)
    cells = _get_notebook_cells()
    if not cells: return

    # Improved ID extraction: checking multiple possible metadata fields
    ids = []
    unknown_detected = False
    for c in cells:
        meta = c.get('metadata', {})
        cid = meta.get('colab', {}).get('id') or c.get('id') or meta.get('id') or 'unknown'
        if cid == 'unknown': unknown_detected = True
        ids.append(str(cid))

    if unknown_detected:
        print("💡 Hint: Some Cell IDs are 'unknown'. Please press Ctrl+S to save the notebook and refresh IDs.")

    max_id_len = max([len(i) for i in ids]) if ids else 12

    jump_base = "[Jump](#scrollTo=)"
    w_jump = max(len("Jump Link"), max_id_len + len(jump_base))
    w_id = max(len("Cell ID"), max_id_len + 2)

    h_jump = f" {('Jump Link').ljust(w_jump)} |" if show_jump_links else ""
    s_jump = f" {(':---').ljust(w_jump, '-')} |" if show_jump_links else ""
    header = f"| Type | Index |{h_jump} {('Cell ID').ljust(w_id)} | Heading / Preview |"
    sep = f"| :--- | :--- |{s_jump} {(':---').ljust(w_id, '-')} | :--- |"

    md_table = ["# TOC Preview. Quick Navigation", f"Filter: `{filter_type}`, Mode: `{'ID' if strict_id_match else 'Content'}`", header, sep]
    match_count = 0

    for idx, cell in enumerate(cells):
        c_type = cell.get("cell_type", "unknown")
        if "All" not in str(filter_type):
            if "Code" in filter_type and c_type != "code": continue
            if "Text" in filter_type and c_type != "markdown": continue

        cell_id = ids[idx]
        source = "".join(cell.get("source", ""))
        if keyword:
            if strict_id_match and keyword != cell_id: continue
            elif not strict_id_match and keyword.lower() not in source.lower(): continue

        match_count += 1
        preview = _extract_heading_preview(source, c_type, stored_limit)
        icon = "MD" if c_type == "markdown" else "Code"
        row = f"| {icon} | {idx:03d} |"
        if show_jump_links: row += f" {f'[Jump](#scrollTo={cell_id})'.ljust(w_jump)} |"
        row += f" {f'`{cell_id}`'.ljust(w_id)} | {preview} |"
        md_table.append(row)

    full_md = "\n".join(md_table)
    if save_log:
        with open("TOC Preview.md", "w", encoding="utf-8", errors="replace") as f: f.write(full_md)
    if show_stats: print(f"Total {len(cells)} cells | Found {match_count} matches.")

    js_md = json.dumps(full_md)
    btn_html = """<div style='margin: 15px 0;'><button id='copy_btn_mod' style='background: #4285f4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;'>Copy TOC to Clipboard</button></div><script>(function(){ const btn = document.getElementById('copy_btn_mod'); btn.onclick = function(){ const text = """ + js_md + """; navigator.clipboard.writeText(text).then(() => { btn.innerText = 'Copied!'; btn.style.background = '#34a853'; setTimeout(() => { btn.innerText = 'Copy TOC to Clipboard'; btn.style.background = '#4285f4'; }, 2000); }); }; })();</script>"""
    display(HTML(btn_html))
    print("\n" + full_md)
