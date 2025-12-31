"""Anki deck and note creation using genanki."""

import os
import tempfile
from pathlib import Path

import genanki

from .cub_adventures.schema import Adventure
from .log import get_logger
from .merit_badges.schema import MeritBadge
from .schema import slug, stable_id


def create_merit_badge_model(model_name: str) -> genanki.Model:
    """Create the Anki model for merit badge cards.

    Args:
        model_name: Name of the model

    Returns:
        Configured genanki Model
    """
    model_id = stable_id(model_name)

    # Base fields
    fields = [
        {"name": "Image"},
        {"name": "Name"},
        {"name": "Description"},
        {"name": "EagleRequired"},
        {"name": "LabNote"},
    ]

    # Front template (Image → Name + Description)
    front_template = """
<div style="text-align: center;">
    {{Image}}
</div>
"""

    back_template = """
{{FrontSide}}
<hr>
<div style="text-align: center;">
    <h2>{{Name}} {{#EagleRequired}}<span class="eagle-badge">🦅</span>{{/EagleRequired}}</h2>
    <p>{{Description}}</p>
    {{#LabNote}}<p class="lab-note">{{LabNote}}</p>{{/LabNote}}
</div>
"""

    templates = [
        {
            "name": "Image → Name + Description",
            "qfmt": front_template,
            "afmt": back_template,
        }
    ]

    # CSS styling
    css = """
    .card {
        font-family: Arial, sans-serif;
        font-size: 16px;
        text-align: center;
        color: black;
        background-color: white;
    }

    h2 {
        color: #2c5aa0;
        margin: 10px 0;
    }

    p {
        margin: 10px 20px;
        line-height: 1.4;
    }

    img {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    hr {
        border: none;
        border-top: 1px solid #ccc;
        margin: 15px 0;
    }

    .eagle-badge {
        color: #b8860b;
        font-size: 0.9em;
        margin-left: 5px;
    }

    .lab-note {
        color: #6b7280;
        font-size: 0.95em;
        margin-top: 8px;
    }
    """

    return genanki.Model(
        model_id=model_id, name=model_name, fields=fields, templates=templates, css=css
    )


def create_merit_badge_note(
    badge: MeritBadge, image_name: str, model: genanki.Model
) -> genanki.Note:
    """Create an Anki note for a merit badge.

    Args:
        badge: Badge data
        image_name: Name of the image file
        model: Anki model to use

    Returns:
        Configured genanki Note
    """
    # Create GUID from badge name and image
    badge_slug = slug(badge.name)
    image_basename = os.path.basename(image_name)
    guid = genanki.guid_for(f"{badge_slug}|{image_basename}")

    # Prepare fields - put complete img tag with styling in the field
    lab_note = "Test Lab Merit Badge" if badge.is_lab else ""
    fields = [
        f'<img src="{image_name}" style="max-width: 85%; height: auto;">',  # Image with styling
        badge.name,  # Name
        badge.description or "",  # Description
        "1" if badge.eagle_required else "",  # EagleRequired (non-empty for true)
        lab_note,
    ]

    tags = ["test-lab"] if badge.is_lab else []
    return genanki.Note(model=model, fields=fields, guid=guid, tags=tags)


def create_merit_badge_deck(
    deck_name: str,
    model_name: str,
    mapped_badges: list[tuple[MeritBadge, str]],
    available_images: dict[str, Path],
) -> tuple[genanki.Deck, list[str]]:
    """Create an Anki deck with merit badge notes.

    Args:
        deck_name: Name of the deck
        model_name: Name of the model
        mapped_badges: List of (badge, image_name) tuples
        available_images: Dict mapping image names to file paths

    Returns:
        Tuple of (deck, list of media file paths)
    """
    logger = get_logger()

    # Create model
    model = create_merit_badge_model(model_name)

    # Create deck
    deck_id = stable_id(deck_name)
    deck = genanki.Deck(deck_id=deck_id, name=deck_name)

    # Create temporary directory for media files
    temp_dir = tempfile.mkdtemp(prefix="scout_anki_")
    media_files = []

    # Create notes
    for badge, image_name in mapped_badges:
        # Copy image file to temp directory
        source_path = available_images[image_name]
        image_path = os.path.join(temp_dir, image_name)

        import shutil

        shutil.copy2(source_path, image_path)
        media_files.append(image_path)

        # Create note
        note = create_merit_badge_note(badge=badge, image_name=image_name, model=model)
        deck.add_note(note)

    logger.info(f"Created deck '{deck_name}' with {len(mapped_badges)} notes")

    return deck, media_files


def write_anki_package(deck: genanki.Deck, media_files: list[str], output_path: str) -> None:
    """Write Anki package to file.

    Args:
        deck: Anki deck to write
        media_files: List of media file paths
        output_path: Output file path
    """
    logger = get_logger()

    # Create package
    package = genanki.Package(deck)
    package.media_files = media_files

    # Write to file
    package.write_to_file(output_path)

    logger.info(f"Wrote Anki package to: {output_path}")


def cleanup_temp_files(media_files: list[str]) -> None:
    """Clean up temporary media files.

    Args:
        media_files: List of temporary file paths to clean up
    """
    logger = get_logger()

    for file_path in media_files:
        try:
            os.unlink(file_path)
        except OSError as e:
            logger.warning(f"Failed to clean up temp file {file_path}: {e}")

    # Try to remove temp directory if empty
    if media_files:
        temp_dir = os.path.dirname(media_files[0])
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass  # Directory not empty or other error, ignore


def create_adventure_model(model_name: str) -> genanki.Model:
    """Create the Anki model for adventure cards."""
    model_id = stable_id(model_name)

    fields = [
        {"name": "Image"},
        {"name": "Name"},
        {"name": "Rank"},
        {"name": "Type"},
        {"name": "Overview"},
    ]

    templates = [
        {
            "name": "Adventure Card",
            "qfmt": """
                <div style="text-align: center; font-family: Arial, sans-serif;">
                    {{Image}}
                </div>
            """,
            "afmt": """
                <div style="text-align: center; font-family: Arial, sans-serif;">
                    {{Image}}
                    <hr>
                    <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">
                        {{Name}}
                    </div>
                    <div style="font-size: 18px; color: #666; margin: 5px 0;">
                        {{Rank}} • {{Type}}
                    </div>
                    <div style="font-size: 14px; margin: 15px 0; text-align: left;
                                max-width: 600px; margin-left: auto; margin-right: auto;">
                        {{Overview}}
                    </div>
                </div>
            """,
        }
    ]

    css = """
        .card {
            font-family: Arial, sans-serif;
            font-size: 16px;
            text-align: center;
            color: black;
            background-color: white;
        }
        img {
            max-width: 85%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    """

    return genanki.Model(
        model_id=model_id,
        name=model_name,
        fields=fields,
        templates=templates,
        css=css,
    )


def create_adventure_deck(
    deck_name: str,
    model_name: str,
    mapped_adventures: list[tuple[Adventure, str]],
    available_images: dict[str, Path],
) -> tuple[genanki.Deck, list[str]]:
    """Create Anki deck for Cub Scout adventures."""
    logger = get_logger()

    # Create model and deck
    model = create_adventure_model(model_name)
    deck_id = stable_id(deck_name)
    deck = genanki.Deck(deck_id=deck_id, name=deck_name)

    # Create temporary directory for media files
    temp_dir = tempfile.mkdtemp()
    media_files = []

    for adventure, image_name in mapped_adventures:
        # Copy image to temp directory
        source_path = available_images[image_name]
        temp_image_path = os.path.join(temp_dir, image_name)

        try:
            import shutil

            shutil.copy2(source_path, temp_image_path)
            media_files.append(temp_image_path)
        except Exception as e:
            logger.warning(f"Failed to copy image {image_name}: {e}")
            continue

        # Create note
        note_id = adventure.stable_id

        # Truncate overview if too long
        overview = adventure.overview
        if len(overview) > 500:
            overview = overview[:497] + "..."

        fields = [
            f'<img src="{image_name}" style="max-width: 85%; height: auto;">',
            adventure.name,
            adventure.rank,
            adventure.type,
            overview,
        ]

        note = genanki.Note(
            model=model,
            fields=fields,
            guid=str(note_id),
        )

        deck.add_note(note)

    logger.info(f"Created deck '{deck_name}' with {len(deck.notes)} notes")
    return deck, media_files
