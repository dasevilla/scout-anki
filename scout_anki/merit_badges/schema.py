"""Merit badge model and JSON schema normalization."""

from dataclasses import dataclass
from typing import Any


@dataclass
class MeritBadge:
    """Merit badge model."""

    name: str
    description: str
    image: str | None = None
    image_filename: str | None = None
    source: str | None = None
    eagle_required: bool = False
    is_lab: bool = False


def normalize_badge_data(data: Any) -> list[MeritBadge]:
    """Normalize JSON data into MeritBadge objects.

    Args:
        data: Raw JSON data (list or dict)

    Returns:
        List of normalized MeritBadge objects
    """
    badges: list[MeritBadge] = []

    # Extract badge list from various JSON structures
    if isinstance(data, list):
        badge_list = data
    elif isinstance(data, dict):
        # Try common keys for badge lists
        for key in ["badges", "items", "data", "meritBadges"]:
            if key in data:
                badge_list = data[key]
                break
        else:
            # If no known key found, treat the dict as a single badge
            badge_list = [data]
    else:
        return badges

    seen_names = set()

    for item in badge_list:
        if not isinstance(item, dict):
            continue

        # Extract name (required)
        name = None
        for name_key in ["name", "title", "badge"]:
            if item.get(name_key):
                name = str(item[name_key]).strip()
                break

        if not name:
            continue  # Skip badges without names

        # Skip duplicates (keep first occurrence)
        if name in seen_names:
            continue
        seen_names.add(name)

        # Extract description
        description = ""
        for desc_key in ["overview", "description", "blurb", "summary"]:
            if item.get(desc_key):
                description = str(item[desc_key]).strip()
                break

        # Extract image filename
        image = None
        for img_key in ["image", "img", "icon"]:
            if item.get(img_key):
                image = str(item[img_key]).strip()
                break

        # Extract image filename
        image_filename = None
        if item.get("image_filename"):
            image_filename = str(item["image_filename"]).strip()

        # Extract eagle required status
        eagle_required = bool(item.get("is_eagle_required", False))
        is_lab = bool(item.get("is_lab", False))

        badge = MeritBadge(
            name=name,
            description=description,
            image=image,
            image_filename=image_filename,
            source="JSON",
            eagle_required=eagle_required,
            is_lab=is_lab,
        )
        badges.append(badge)

    return badges
