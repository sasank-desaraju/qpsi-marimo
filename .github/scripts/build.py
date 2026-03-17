# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "jinja2==3.1.3",
#     "loguru==0.7.0",
# ]
# ///

"""
Build script for QPSI marimo notebooks.

Exports all notebooks in notebooks/ to HTML/WASM as apps (run mode, code hidden)
and generates an index.html landing page.

Usage:
    uv run .github/scripts/build.py
"""

import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

MARIMO_VERSION = "0.21.0"
OUTPUT_DIR = Path("_site")
NOTEBOOKS_DIR = Path("notebooks")
TEMPLATE_FILE = Path("templates/index.html.j2")


def export_notebook(notebook_path: Path, output_dir: Path) -> bool:
    """Export a single marimo notebook to HTML/WASM in run mode (code hidden)."""
    output_file = output_dir / notebook_path.with_suffix(".html")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "uvx", f"marimo=={MARIMO_VERSION}",
        "export", "html-wasm",
        "--sandbox",
        "--mode", "run",
        "--no-show-code",
        str(notebook_path),
        "-o", str(output_file),
    ]

    logger.info(f"Exporting {notebook_path} -> {output_file}")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Success: {notebook_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {notebook_path}\n{e.stderr}")
        return False


def generate_index(apps: list[dict], output_dir: Path) -> None:
    """Generate index.html from the Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILE.parent),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(TEMPLATE_FILE.name)
    html = template.render(apps=apps)

    index_path = output_dir / "index.html"
    index_path.write_text(html)
    logger.info(f"Generated {index_path}")


def main() -> None:
    logger.info("Starting QPSI marimo build")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create .nojekyll to prevent GitHub Pages from processing with Jekyll
    (OUTPUT_DIR / ".nojekyll").touch()

    notebooks = sorted(NOTEBOOKS_DIR.glob("*.py"))
    if not notebooks:
        logger.warning("No notebooks found!")
        return

    apps_data = []
    for nb in notebooks:
        if export_notebook(nb, OUTPUT_DIR):
            apps_data.append({
                "display_name": nb.stem.replace("_", " ").title(),
                "html_path": str(nb.with_suffix(".html")),
            })

    logger.info(f"Exported {len(apps_data)}/{len(notebooks)} notebooks")

    generate_index(apps_data, OUTPUT_DIR)
    logger.info("Build complete")


if __name__ == "__main__":
    main()
