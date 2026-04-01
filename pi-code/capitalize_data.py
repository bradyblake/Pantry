"""
Capitalize (title-case) all pantry item names, categories, locations,
and recipe titles in the database.

Safety: This script ONLY updates text casing. It does NOT delete any rows
or modify any quantities/relationships. A backup should already exist at:
  /mnt/usb/recipe-manager/data/recipes.db.backup-*

Usage: python3 capitalize_data.py [--dry-run]
  --dry-run  Show what would change without writing to the database
"""
import sys
import sqlite3
import os

# Resolve database path the same way config.py does
from dotenv import load_dotenv
load_dotenv()
DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "data", "recipes.db"))


def title_case(s):
    """Title-case a string, handling edge cases."""
    if not s or not s.strip():
        return s
    # Title case but preserve all-caps words (abbreviations like PB, BBQ)
    words = s.split()
    result = []
    for w in words:
        if w.isdigit():
            result.append(w)
        elif w.isupper() and len(w) >= 2:
            # Preserve all-caps abbreviations like PB, BBQ, etc.
            result.append(w)
        elif '-' in w:
            # Handle hyphenated words: capitalize each part
            result.append('-'.join(part.capitalize() for part in w.split('-')))
        elif '/' in w:
            result.append('/'.join(part.capitalize() for part in w.split('/')))
        elif '(' in w:
            # Handle parenthesized words
            result.append(w[0] + w[1:].capitalize() if len(w) > 1 else w)
        else:
            result.append(w.capitalize())
    # Always capitalize first word
    if result:
        first = result[0]
        if not first[0:1].isupper() and first not in ('&',):
            result[0] = first.capitalize()
    return ' '.join(result)


def main():
    dry_run = '--dry-run' in sys.argv

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    changes = []

    # Pantry items: name, category, location
    cursor.execute("SELECT id, name, category, location FROM pantry_items")
    for row in cursor.fetchall():
        item_id, name, category, location = row
        new_name = title_case(name)
        new_cat = title_case(category) if category else category
        new_loc = title_case(location) if location else location
        if new_name != name or new_cat != category or new_loc != location:
            changes.append(('pantry_items', item_id, name, new_name, category, new_cat, location, new_loc))
            if not dry_run:
                cursor.execute(
                    "UPDATE pantry_items SET name=?, category=?, location=? WHERE id=?",
                    (new_name, new_cat, new_loc, item_id)
                )

    # Recipe titles
    cursor.execute("SELECT id, title FROM recipes")
    for row in cursor.fetchall():
        recipe_id, title = row
        new_title = title_case(title)
        if new_title != title:
            changes.append(('recipes', recipe_id, title, new_title, '', '', '', ''))
            if not dry_run:
                cursor.execute("UPDATE recipes SET title=? WHERE id=?", (new_title, recipe_id))

    # Recipe ingredient names
    cursor.execute("SELECT id, name FROM recipe_ingredients")
    for row in cursor.fetchall():
        ing_id, name = row
        new_name = title_case(name)
        if new_name != name:
            changes.append(('recipe_ingredients', ing_id, name, new_name, '', '', '', ''))
            if not dry_run:
                cursor.execute("UPDATE recipe_ingredients SET name=? WHERE id=?", (new_name, ing_id))

    # Tag names
    cursor.execute("SELECT id, name FROM tags")
    for row in cursor.fetchall():
        tag_id, name = row
        new_name = title_case(name)
        if new_name != name:
            changes.append(('tags', tag_id, name, new_name, '', '', '', ''))
            if not dry_run:
                cursor.execute("UPDATE tags SET name=? WHERE id=?", (new_name, tag_id))

    if not dry_run:
        conn.commit()

    conn.close()

    # Print summary
    mode = "DRY RUN - " if dry_run else ""
    print(f"\n{mode}Capitalization complete!")
    print(f"Total changes: {len(changes)}")
    if changes:
        print("\nChanges:")
        for table, item_id, old, new, *rest in changes:
            print(f"  [{table} #{item_id}] '{old}' -> '{new}'")
            if rest[0] or rest[2]:
                if rest[0] != rest[1]:
                    print(f"    category: '{rest[0]}' -> '{rest[1]}'")
                if rest[2] != rest[3]:
                    print(f"    location: '{rest[2]}' -> '{rest[3]}'")
    else:
        print("No changes needed - everything is already capitalized!")


if __name__ == "__main__":
    main()
