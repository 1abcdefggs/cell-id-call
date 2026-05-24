# Cell ID Call

**Version: 0.2.0**
In Google Colab, cell IDs (the unique identifiers for each code or text cell) can change when you add, delete, or reorder cells. This often leads to broken anchor links in your Table of Contents, making it difficult to navigate within your notebook. This tool was developed to solve this problem by generating stable, persistent anchor links.

## Project Structure
```
cell-id-call/
├── src/                    # Module version
│   ├── __init__.py
│   └── toc_generator.py    # Core TOC generation logic
├── scripts/                # Standalone version
│   └── standalone_toc.py   # Standalone script for Gist distribution
├── notebooks/              # Development notebooks
│   └── cell_id_call.ipynb # Main development notebook
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Usage

### Module Version
```python
import sys
sys.path.append('src')
import toc_generator

toc_generator.set_toc_len(70)
toc_generator.generate_advanced_toc(
    filter_type="All",
    keyword="",
    show_stats=True,
    strict_id_match=False,
    show_jump_links=True,
    save_log=True
)
```

### Standalone Version
Copy the code from [GitHub Gist](https://gist.github.com/1abcdefggs/21632dd1f3670e8d1506e4788ab514cc) to your Colab notebook and run it directly.

## Generate: Table of Contents for Cell IDs
<img width="689" height="376" alt="image" src="https://github.com/user-attachments/assets/9651799a-d1c4-40b8-9bc2-e7b646be0a20" />
