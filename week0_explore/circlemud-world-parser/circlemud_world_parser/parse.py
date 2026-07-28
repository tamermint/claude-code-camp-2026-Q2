import json
import logging
from pathlib import Path
from typing import Optional

import typer

from .mobile import Mobile
from .object import Object
from .quest import Quest
from .room import Room
from .shop import Shop
from .trigger import Trigger
from .utils import parse_from_file, split_on_vnums
from .zone import Zone

app = typer.Typer()

PARSER_LOOKUP = {
    'mob': (Mobile.from_text, split_on_vnums),
    'obj': (Object.from_text, split_on_vnums),
    'wld': (Room.from_text, split_on_vnums),
    'shp': (Shop.from_text, split_on_vnums),
    'zon': (Zone.from_text, split_on_vnums),
    'trg': (Trigger.from_text, split_on_vnums),
    'qst': (Quest.from_text, split_on_vnums),
}


def indent(text):
    lines = text.split('\n')
    indented = ['\t' + line for line in lines]
    new_text = '\n'.join(indented)
    return new_text


def log_errors(errors):
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)

    for error in errors:
        text, trace = indent(error['text']), indent(error['trace'])
        logger.error('Error parsing:\n\n%s\n%s', text, trace)


def get_file_type(filepath):
    return Path(filepath).suffix.lstrip('.')


def parse_based_on_filepath(filepath):
    # figure out which type of tinyworld file we've been pointed at
    file_type = get_file_type(filepath)

    if file_type not in PARSER_LOOKUP:
        fmt = 'No parser found for file type: "{}"'
        raise RuntimeError(fmt.format(file_type))

    parser, splitter = PARSER_LOOKUP[file_type]
    payload, errors = parse_from_file(filepath, parser, splitter)

    return payload, errors


@app.command()
def parse(
    src: str = typer.Option(..., help="source directory containing world files"),
    dest: str = typer.Option(..., help="destination directory for json output"),
):
    src_path = Path(src)
    dest_path = Path(dest)
    
    total_files = 0
    errors_encountered = 0

    for file_path in src_path.rglob('*'):
        if not file_path.is_file():
            continue
            
        file_type = get_file_type(file_path)
        if file_type not in PARSER_LOOKUP:
            continue

        total_files += 1
        print(f"Parsing: {file_path.name}")
        
        try:
            payload, errors = parse_based_on_filepath(file_path)
            if errors:
                log_errors(errors)
                errors_encountered += len(errors)

            if payload:
                payload_dicts = [item.model_dump() for item in payload]
                payload_json = json.dumps(payload_dicts, indent=2, sort_keys=True)
                
                # Create subfolder and write file
                out_dir = dest_path / file_type
                out_dir.mkdir(parents=True, exist_ok=True)
                
                out_file = out_dir / f"{file_path.stem}.json"
                with open(out_file, 'w') as f:
                    f.write(payload_json)
                    
        except Exception as e:
            print(f"CRITICAL ERROR parsing {file_path.name}: {e}")
            errors_encountered += 1
            
    print(f"\nBatch Complete. Processed {total_files} files with {errors_encountered} extraction errors.")


if __name__ == '__main__':
    app()
