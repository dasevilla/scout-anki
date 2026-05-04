"""Tests for cub adventure functionality."""

import json
import tempfile
from pathlib import Path

from scout_anki.cub_adventures.processor import AdventureProcessor
from scout_anki.schema import stable_id


def test_cub_adventure_directory_processing():
    """Test processing directory with cub adventure data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create rank directory structure
        tiger_dir = test_dir / "tiger"
        tiger_dir.mkdir()
        images_dir = tiger_dir / "images"
        images_dir.mkdir()

        # Create test adventure data with expected field names
        adventure_data = {
            "adventure_name": "Backyard Jungle",
            "rank_name": "Tiger",
            "adventure_type": "Adventure",
            "adventure_overview": "Explore nature",
            "image_filename": "jungle.png",
        }

        # Write JSON file in rank directory
        (tiger_dir / "backyard-jungle.json").write_text(json.dumps(adventure_data))

        # Create image file in images subdirectory
        (images_dir / "jungle.png").write_bytes(b"fake jungle image")

        # Process directory
        processor = AdventureProcessor()
        adventures, images = processor.process_directory(str(test_dir))

        assert len(adventures) == 1
        assert len(images) == 1
        assert adventures[0].name == "Backyard Jungle"
        assert "jungle.png" in images


def test_cub_adventure_combined_archive_root_ignores_requirements_and_other_images():
    """Test processing Cub adventures from a combined scout-archive root."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        adventure_dir = test_dir / "cub-adventure" / "bear"
        adventure_images_dir = adventure_dir / "images"
        merit_images_dir = test_dir / "merit-badge" / "images"
        adventure_images_dir.mkdir(parents=True)
        merit_images_dir.mkdir(parents=True)

        adventure_data = {
            "adventure_name": "A Bear Goes Fishing",
            "rank_name": "Bear",
            "adventure_type": "Elective",
            "adventure_overview": "Learn about fishing and local fish.",
            "image_filename": "a-bear-goes-fishing.jpg",
            "requirements": [
                {
                    "label": "1",
                    "text": "Learn about three types of fish in your area.",
                    "requirement_path": "1",
                    "node_kind": "action_requirement",
                    "is_container": False,
                    "requires_response": True,
                    "resources": [],
                    "sub_requirements": [],
                    "activities": [
                        {
                            "name": "Types of Fish",
                            "url": "https://www.scouting.org/cub-scout-activities/types-of-fish/",
                        }
                    ],
                }
            ],
        }

        (adventure_dir / "a-bear-goes-fishing.json").write_text(json.dumps(adventure_data))
        (adventure_images_dir / "a-bear-goes-fishing.jpg").write_bytes(b"fake adventure image")
        (merit_images_dir / "merit-only.jpg").write_bytes(b"fake merit image")

        processor = AdventureProcessor()
        adventures, images = processor.process_directory(str(test_dir))

        assert len(adventures) == 1
        assert adventures[0].name == "A Bear Goes Fishing"
        assert adventures[0].rank == "Bear"
        assert len(images) == 1
        assert "a-bear-goes-fishing.jpg" in images
        assert "merit-only.jpg" not in images


def test_cub_adventure_stable_id_is_deterministic():
    """Test adventure note IDs do not use Python's randomized hash."""
    from scout_anki.cub_adventures.schema import Adventure

    adventure = Adventure(
        name="A Bear Goes Fishing",
        rank="Bear",
        type="Elective",
        overview="Learn about fishing.",
    )

    assert adventure.stable_id == stable_id("adventure:Bear:A Bear Goes Fishing") % (2**31)


def test_cub_adventure_build_parent_root():
    """Test processing Cub adventures from the scout-archive build parent."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        adventure_dir = test_dir / "cub-scout-adventures" / "tiger"
        images_dir = adventure_dir / "images"
        images_dir.mkdir(parents=True)

        adventure_data = {
            "adventure_name": "Backyard Jungle",
            "rank_name": "Tiger",
            "adventure_type": "Adventure",
            "adventure_overview": "Explore nature",
            "image_filename": "jungle.png",
        }

        (adventure_dir / "backyard-jungle.json").write_text(json.dumps(adventure_data))
        (images_dir / "jungle.png").write_bytes(b"fake jungle image")

        processor = AdventureProcessor()
        adventures, images = processor.process_directory(str(test_dir))

        assert len(adventures) == 1
        assert adventures[0].name == "Backyard Jungle"
        assert len(images) == 1
        assert "jungle.png" in images


def test_cub_adventure_empty_directory():
    """Test processing empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        processor = AdventureProcessor()
        adventures, images = processor.process_directory(temp_dir)

        assert len(adventures) == 0
        assert len(images) == 0


def test_cub_adventure_defaults():
    """Test cub adventure processor defaults."""
    processor = AdventureProcessor()
    defaults = processor.get_defaults()

    assert defaults["out"] == "cub_scout_adventure_image_trainer.apkg"
    assert defaults["deck_name"] == "Cub Scout Adventure Image Trainer"
    assert defaults["model_name"] == "Cub Scout Adventure Quiz"


def test_cub_adventure_mapping():
    """Test cub adventure to image mapping."""
    processor = AdventureProcessor()

    # Mock adventure data
    from scout_anki.cub_adventures.schema import Adventure

    adventures = [
        Adventure(
            name="Backyard Jungle",
            rank="Tiger",
            type="Adventure",
            overview="Test",
            image_filename="jungle.png",
        )
    ]
    images = {"jungle.png": Path("jungle.png")}

    mapped, unmapped = processor.map_content_to_images(adventures, images)

    assert len(mapped) == 1
    assert len(unmapped) == 0
    assert mapped[0][0].name == "Backyard Jungle"
    assert mapped[0][1] == "jungle.png"
