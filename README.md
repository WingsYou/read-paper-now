# Read Paper Now

A command-line tool and Typora plugin to automatically fetch paper information (title, authors, year, venue, citations) from arXiv, Google Scholar, Semantic Scholar, and OpenReview.

**Perfect for managing your research paper reading notes in Typora!**

## Features

- 🔍 **Multi-source support**: arXiv, Google Scholar, Semantic Scholar, OpenReview, DOI
- 📊 **Auto-fetch citations**: Get citation counts automatically
- 📝 **Formatted output**: `**Paper Title** FirstAuthor et al. Year. Venue. Citations: N`
- ⚡ **Typora integration**: Right-click to fetch paper info directly in your markdown editor
- 🔄 **Smart fallback**: Automatically tries multiple sources for best results

## Quick Start

### 1. Installation

```bash
git clone https://github.com/YOUR_USERNAME/read_paper_now.git
cd read_paper_now
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Fetch paper info from arXiv
python fetch_paper_info.py "https://arxiv.org/abs/1706.03762"

# Output: **Attention Is All You Need** Vaswani, A. et al. 2017. NeurIPS. Citations: 98234
```

### 3. Advanced Options

```bash
# Search by title using Google Scholar
python fetch_paper_info.py "Attention Is All You Need" --google-scholar

# Prioritize Google Scholar for citation counts (more accurate)
python fetch_paper_info.py "https://arxiv.org/abs/1706.03762" --use-google-scholar-citations

# Show more authors
python fetch_paper_info.py "URL" --max-authors 5

# Debug mode
python fetch_paper_info.py "URL" --debug
```

## Typora Integration

Transform your paper reading workflow! Select a paper URL in Typora, right-click, and get formatted paper info instantly.

### Setup (macOS)

**Step 1:** Find your Typora config file location

```bash
~/Library/Application Support/abnerworks.Typora/conf/conf.user.json
```

If it doesn't exist, create it:
```bash
mkdir -p ~/Library/Application\ Support/abnerworks.Typora/conf/
touch ~/Library/Application\ Support/abnerworks.Typora/conf/conf.user.json
```

**Step 2:** Add this configuration (replace `/path/to/` with your actual path):

```json
{
  "customCommand": {
    "arxiv-paper-info": {
      "name": "Fetch Paper Info",
      "command": "/path/to/read_paper_now/typora-plugin/fetch_and_replace.sh",
      "args": ["${selection}"],
      "replaceSelection": true,
      "when": "hasSelection"
    }
  }
}
```

**Step 3:** Make the script executable

```bash
chmod +x /path/to/read_paper_now/typora-plugin/fetch_and_replace.sh
```

**Step 4:** Restart Typora

### Setup (Linux)

Config file location: `~/.config/Typora/conf/conf.user.json`

Follow the same steps as macOS.

### Setup (Windows)

Config file location: `%APPDATA%\Typora\conf\conf.user.json`

```json
{
  "customCommand": {
    "arxiv-paper-info": {
      "name": "Fetch Paper Info",
      "command": "C:\\path\\to\\read_paper_now\\typora-plugin\\fetch_and_replace.bat",
      "args": ["${selection}"],
      "replaceSelection": true,
      "when": "hasSelection"
    }
  }
}
```

**Note:** Use double backslashes `\\` in Windows paths.

### Using in Typora

1. **Select** a paper URL in Typora (e.g., `https://arxiv.org/abs/1706.03762`)
2. **Right-click** → **"Fetch Paper Info"**
3. The URL will be replaced with formatted paper information! ✨

Example:
```markdown
Before: https://arxiv.org/abs/1706.03762

After: **Attention Is All You Need** Vaswani, A. et al. 2017. NeurIPS. Citations: 98234
```

## Supported Sources

- ✅ **arXiv** - `https://arxiv.org/abs/XXXX.XXXXX`
- ✅ **Google Scholar** - Search by title or fetch accurate citation counts
- ✅ **Semantic Scholar** - Fast API-based fetching
- ✅ **OpenReview** - `https://openreview.net/forum?id=XXXXX`
- ✅ **DOI** - `https://doi.org/10.XXXX/...`

## Output Format

The tool outputs in academic citation format:

```
**Paper Title** LastName, Initials., LastName2, Initials2, and LastName3, Initials3 et al. Year. Venue. Citations: N
```

Examples:
- 1 author: `**Title** Smith, J. 2023. NeurIPS. Citations: 100`
- 2 authors: `**Title** Smith, J. and Doe, A. 2023. ICLR. Citations: 50`
- 3+ authors: `**Title** Smith, J. et al. 2023. arXiv. Citations: 10`

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--max-authors N` | Show up to N authors (default: 3) |
| `--google-scholar` | Search by paper title using Google Scholar |
| `--use-google-scholar-citations` | Prioritize Google Scholar for citation counts |
| `--debug` | Show debug information for troubleshooting |
| `--test` | Offline test mode with sample data |

## Requirements

- Python 3.7+
- `requests` >= 2.31.0
- `beautifulsoup4` >= 4.12.0

## Project Structure

```
read_paper_now/
├── fetch_paper_info.py          # Main script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── LICENSE                      # MIT License
└── typora-plugin/               # Typora integration files
    ├── fetch_and_replace.sh     # Shell wrapper (macOS/Linux)
    └── fetch_and_replace.bat    # Batch wrapper (Windows)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Acknowledgments

- Built for researchers and students managing paper reading notes
- Inspired by the need for efficient paper information management in markdown editors
- Uses arXiv, Semantic Scholar, and Google Scholar APIs/web scraping

---

Inspired by Mu Li, a great AI researcher. If this tool helped you, please ⭐ star the repo!
