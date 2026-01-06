#!/usr/bin/env python3
"""
Deploy RSS Feed to GitHub Pages

Exports RSS feed and copies it to the docs/ directory for GitHub Pages hosting.
"""
import sys
import shutil
from pathlib import Path


def main():
    """Deploy RSS feed and HTML pages to GitHub Pages docs directory."""
    print("=" * 70)
    print("Deploying to GitHub Pages")
    print("=" * 70)

    # Step 1: Generate HTML pages from digests
    print("\n[1/3] Generating HTML pages...")

    # Import and run generate_html
    import generate_html
    result = generate_html.main()

    if result != 0:
        print("\n✗ HTML generation failed")
        return 1

    # Step 2: Export RSS feed
    print("\n[2/3] Generating RSS feed...")

    # Import and run export_rss
    import export_rss
    result = export_rss.main()

    if result != 0:
        print("\n✗ RSS export failed")
        return 1

    # Step 3: Copy feed to docs directory
    print("\n[3/3] Copying feed to docs/ directory...")

    source = Path('output/digest_feed.xml')
    dest_dir = Path('docs')
    dest = dest_dir / 'digest_feed.xml'

    if not source.exists():
        print(f"✗ Source file not found: {source}")
        return 1

    # Ensure docs directory exists
    dest_dir.mkdir(exist_ok=True)

    # Copy file
    shutil.copy2(source, dest)
    print(f"  ✓ Copied to: {dest}")

    # Summary
    print("\n" + "=" * 70)
    print("Deployment Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Commit the changes:")
    print("   git add docs/")
    print("   git commit -m 'Update RSS feed and HTML pages'")
    print("   git push")
    print()
    print("2. Enable GitHub Pages (if not already enabled):")
    print("   - Go to repository Settings → Pages")
    print("   - Set Source to 'Deploy from a branch'")
    print("   - Select branch 'main' and folder '/docs'")
    print("   - Save")
    print()
    print("3. View online:")
    print("   Landing: https://mdh2321.github.io/legal-digest/")
    print("   RSS Feed: https://mdh2321.github.io/legal-digest/digest_feed.xml")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
