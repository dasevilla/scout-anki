"""Tests for merit badge functionality."""

import json
import tempfile
from pathlib import Path

from scout_anki.merit_badges.processor import MeritBadgeProcessor


def test_merit_badge_directory_processing():
    """Test processing directory with merit badge data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create test badge data
        badge_data = [
            {
                "name": "Camping",
                "description": "Learn outdoor skills",
                "image_filename": "camping.png",
            },
            {"name": "Hiking", "description": "Trail adventures", "image_filename": "hiking.jpg"},
        ]

        # Write JSON file
        (test_dir / "badges.json").write_text(json.dumps(badge_data))

        # Create image files
        (test_dir / "camping.png").write_bytes(b"fake camping image")
        (test_dir / "hiking.jpg").write_bytes(b"fake hiking image")

        # Process directory
        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(str(test_dir))

        assert len(badges) == 2
        assert len(images) == 2
        assert badges[0].name == "Camping"
        assert "camping.png" in images


def test_merit_badge_combined_archive_root_ignores_requirements_and_other_images():
    """Test processing merit badges from a combined scout-archive root."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        merit_dir = test_dir / "merit-badge"
        merit_images_dir = merit_dir / "images"
        cub_images_dir = test_dir / "cub-adventure" / "tiger" / "images"
        merit_images_dir.mkdir(parents=True)
        cub_images_dir.mkdir(parents=True)

        badge_data = {
            "name": "Citizenship in Society",
            "overview": "Learn about diversity, equity, inclusion, and ethical leadership.",
            "is_eagle_required": True,
            "is_lab": False,
            "image_filename": "citizenship-in-society-merit-badge.jpg",
            "requirements": [
                {
                    "label": "1",
                    "text": "Before beginning work on other requirements for this merit badge.",
                    "requirement_path": "1",
                    "node_kind": "action_requirement",
                    "is_container": False,
                    "requires_response": True,
                    "resources": [],
                    "sub_requirements": [],
                }
            ],
        }

        (merit_dir / "citizenship-in-society-merit-badge.json").write_text(json.dumps(badge_data))
        (merit_images_dir / "citizenship-in-society-merit-badge.jpg").write_bytes(
            b"fake badge image"
        )
        (cub_images_dir / "cub-only.jpg").write_bytes(b"fake cub image")

        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(str(test_dir))

        assert len(badges) == 1
        assert badges[0].name == "Citizenship in Society"
        assert badges[0].description.startswith("Learn about diversity")
        assert badges[0].eagle_required is True
        assert len(images) == 1
        assert "citizenship-in-society-merit-badge.jpg" in images
        assert "cub-only.jpg" not in images


def test_merit_badge_build_parent_root():
    """Test processing merit badges from the scout-archive build parent."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        merit_dir = test_dir / "merit-badges"
        merit_dir.mkdir()

        badge_data = {
            "name": "Camping",
            "overview": "Learn outdoor skills",
            "image_filename": "camping.png",
        }

        (merit_dir / "camping.json").write_text(json.dumps(badge_data))
        (merit_dir / "camping.png").write_bytes(b"fake camping image")

        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(str(test_dir))

        assert len(badges) == 1
        assert badges[0].name == "Camping"
        assert len(images) == 1
        assert "camping.png" in images


def test_merit_badge_empty_directory():
    """Test processing empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(temp_dir)

        assert len(badges) == 0
        assert len(images) == 0


def test_merit_badge_defaults():
    """Test merit badge processor defaults."""
    processor = MeritBadgeProcessor()
    defaults = processor.get_defaults()

    assert defaults["out"] == "merit_badges_image_trainer.apkg"
    assert defaults["deck_name"] == "Merit Badges Image Trainer"
    assert defaults["model_name"] == "Merit Badge Quiz"


def test_merit_badge_mapping():
    """Test merit badge to image mapping."""
    processor = MeritBadgeProcessor()

    # Mock badge data
    from scout_anki.merit_badges.schema import MeritBadge

    badges = [MeritBadge(name="Camping", description="Test", image_filename="camping.png")]
    images = {"camping.png": Path("camping.png")}

    mapped, unmapped = processor.map_content_to_images(badges, images)

    assert len(mapped) == 1
    assert len(unmapped) == 0
    assert mapped[0][0].name == "Camping"
    assert mapped[0][1] == "camping.png"
