"""Merit badge processor."""

import json
from pathlib import Path

import click
import genanki

from .. import deck
from ..image_utils import discover_images, map_content_by_image_filename
from ..log import get_logger
from ..processor import DeckProcessor
from .schema import MeritBadge, normalize_badge_data


def _resolve_merit_badge_root(directory: Path) -> Path:
    """Return the directory that contains merit badge JSON and images."""
    for child_name in ("merit-badge", "merit-badges"):
        child = directory / child_name
        if child.is_dir():
            return child
    return directory


class MeritBadgeProcessor(DeckProcessor):
    """Processor for merit badge decks."""

    def __init__(self):
        super().__init__("badges")

    def get_defaults(self) -> dict[str, str]:
        """Get default values for merit badges."""
        return {
            "out": "merit_badges_image_trainer.apkg",
            "deck_name": "Merit Badges Image Trainer",
            "model_name": "Merit Badge Quiz",
        }

    def process_directory(self, directory_path: str) -> tuple[list[MeritBadge], dict[str, Path]]:
        """Process directory to find badges and images."""
        directory = _resolve_merit_badge_root(Path(directory_path))

        # Find and process JSON files
        all_badge_data = []
        for json_file in directory.glob("**/*.json"):
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            # Handle both single objects and arrays
            if isinstance(data, list):
                all_badge_data.extend(data)
            else:
                all_badge_data.append(data)

        # Normalize all badge data
        badges = normalize_badge_data(all_badge_data)

        # Find image files
        available_images = discover_images(directory)

        return badges, available_images

    def map_content_to_images(
        self, content: list[MeritBadge], images: dict[str, Path]
    ) -> tuple[list[tuple[MeritBadge, str]], list[MeritBadge]]:
        """Map badges to images."""
        logger = get_logger()
        mapped_badges, unmapped_badges = map_content_by_image_filename(content, images)

        logger.info(
            f"Mapped {len(mapped_badges)} badges to images, "
            f"{len(unmapped_badges)} badges without images"
        )
        return mapped_badges, unmapped_badges

    def create_mapping_summary(
        self,
        content: list[MeritBadge],
        images: dict[str, Path],
        mapped: list[tuple[MeritBadge, str]],
        unmapped: list[MeritBadge],
    ) -> dict[str, int | list[str]]:
        """Create mapping summary for badges."""
        mapped_image_names = {img_name for _, img_name in mapped}
        unused_images = set(images.keys()) - mapped_image_names

        # Create missing image details
        missing_images = []
        for badge in unmapped:
            expected = getattr(badge, "image_filename", "unknown")
            missing_images.append({"badge_name": badge.name, "expected_image": expected})

        return {
            "total_badges": len(content),
            "total_images": len(images),
            "mapped_badges": len(mapped),
            "unmapped_badges": len(unmapped),
            "unused_images": len(unused_images),
            "missing_image_details": missing_images,
        }

    def print_summary(self, summary: dict[str, int | list[str]], dry_run: bool) -> None:
        """Print merit badge summary."""
        click.echo("\n" + "=" * 60)
        click.echo("BUILD SUMMARY")
        click.echo("=" * 60)

        click.echo(f"Total badges in JSON: {summary['total_badges']}")
        click.echo(f"Total images available: {summary['total_images']}")
        click.echo(f"Badges mapped to images: {summary['mapped_badges']}")
        click.echo(f"Badges without images: {summary['unmapped_badges']}")
        click.echo(f"Unused images: {summary['unused_images']}")

        if summary["missing_image_details"]:
            click.echo(f"\nMissing images ({len(summary['missing_image_details'])}):")
            for item in summary["missing_image_details"]:
                click.echo(f"  • {item['badge_name']} → {item['expected_image']}")

        if dry_run:
            click.echo(f"\n[DRY RUN] Would create deck with {summary['mapped_badges']} notes")

        click.echo("=" * 60)

    def create_deck(
        self,
        deck_name: str,
        model_name: str,
        mapped_content: list[tuple[MeritBadge, str]],
        images: dict[str, Path],
    ) -> tuple[genanki.Deck, list[str]]:
        """Create merit badge deck."""
        return deck.create_merit_badge_deck(deck_name, model_name, mapped_content, images)
