# scout-anki

Anki deck builder for Scouting content. Generates Anki decks for learning Scouting America merit badges and Cub Scout adventures by sight. The front of the card is an image of the merit badge or adventure loop. The back of the card is the name, description, and additional details.

## Usage

### Basic Usage

First, download and extract the scout-archive release files:

```bash
# Download and extract latest release archives for merit badges
make fetch-and-build-merit-badges

# Download and extract latest release archives for cub adventures
make fetch-and-build-cub-adventures

# Build both deck types
make fetch-releases extract-archives build-all
```

This downloads archives, extracts them to `extracted/` directory, and creates `.apkg` files that can be imported into Anki.

The build command accepts the current Scout Archive layouts:

- release archive roots where merit badge JSON/images or Cub rank directories are directly under the directory
- combined archive roots containing `merit-badge/` and `cub-adventure/`
- local scout-archive build roots containing `merit-badges/` and `cub-scout-adventures/`
- any direct content root such as `build/merit-badges` or `build/cub-scout-adventures`

### Manual Usage

```bash
# Download archives
gh release download --repo dasevilla/scout-archive --pattern "*.tar.gz"

# Extract archives
mkdir -p extracted/
for file in *.tar.gz; do tar -xzf "$file" -C extracted/; done

# Generate merit badge Anki deck from extracted directory or combined archive root
scout-anki build merit-badges extracted/

# Generate cub adventure Anki deck from extracted directory or combined archive root
scout-anki build cub-adventures extracted/
```

### Advanced Usage

```bash
# Merit badges with custom output file
scout-anki build merit-badges extracted/ --out my_badges.apkg

# Cub adventures with custom output file
scout-anki build cub-adventures extracted/ --out my_adventures.apkg

# Dry run to preview without creating file
scout-anki build merit-badges extracted/ --dry-run
scout-anki build cub-adventures extracted/ --dry-run

# Custom deck and model names
scout-anki build merit-badges extracted/ --deck-name "My Badges" --model-name "Badge Quiz"
scout-anki build cub-adventures extracted/ --deck-name "My Adventures" --model-name "Adventure Quiz"
```

### Command Reference

#### `build` - Generate Anki deck

```bash
scout-anki build DECK_TYPE DIRECTORY [OPTIONS]
```

**Arguments:**
- `DECK_TYPE` - Type of deck to build: `merit-badges` or `cub-adventures`
- `DIRECTORY` - Directory containing extracted badge data and images, or a parent directory with a recognized Scout Archive content root

**Options:**
- `--out PATH` - Output file path (auto-generated based on deck type if not specified)
- `--deck-name TEXT` - Anki deck name (auto-generated based on deck type if not specified)
- `--model-name TEXT` - Anki model name (auto-generated based on deck type if not specified)
- `--dry-run` - Preview without creating .apkg file
- `-q, --quiet` - Only show errors
- `-v, --verbose` - Increase verbosity

## How It Works

1. **Reads extracted Scout Archive JSON and images** from recognized release and local build layouts
2. **Extracts card metadata** from JSON files using flexible schema normalization
3. **Maps content to images** using direct `image_filename` field mapping
4. **Creates Anki deck** with stable IDs to prevent duplicates on reimport
5. **Bundles media files** into a complete .apkg package

Scout Archive requirement trees are intentionally not turned into cards. Requirement metadata such as `text`, `requirement_path`, `node_kind`, `is_container`, and `requires_response` may be present in the source JSON, but this tool uses only the top-level fields needed for image-recognition flashcards.

### Image Mapping Strategy

The tool uses direct field mapping for reliable image association:

1. **Direct mapping**: Uses the `image_filename` field from JSON data
2. **100% success rate**: All badges and adventures now have explicit image filenames
3. **No pattern matching needed**: Simplified from complex inference logic

### Card Format

**Merit Badges:**
- **Front**: Merit badge image (centered, 85% width)
- **Back**: Badge name, description, and Eagle required indicator

**Cub Adventures:**
- **Front**: Adventure loop image (centered, 85% width)
- **Back**: Adventure name, rank, type, and description

## Development

To contribute to this tool, first checkout the code. Then set up the development environment:

```bash
cd scout-anki
uv sync
```

This will create a virtual environment and install all dependencies including development tools.

To set up pre-commit hooks (recommended):

```bash
make setup-pre-commit
```

To run the tests:

```bash
make test
```

## Data Source

This tool is built using data from the [scout-archive](https://github.com/dasevilla/scout-archive) repository, which is updated roughly weekly.
