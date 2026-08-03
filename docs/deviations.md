## Project specific deviations from initial setup

- tbaMUD raw world files have builder typos so I had to work with gemini to fix the parser logic. The `convert-world.sh` script needed to be changed as well. My OS memory was getting exhausted due to multiple uv runs in the .venv of circlemud-world-parser.
  - `room.py` fix:

    ```python
          import re
    text = text.strip()

    # 1. Extract VNUM safely, ignoring inline builder comments
    match_vnum = re.match(r"^(\d+)(?:\s+|$)(.*)", text, re.DOTALL)
    if not match_vnum:
        raise ValueError("Could not extract VNUM from block")

    vnum = int(match_vnum.group(1))
    remainder = match_vnum.group(2).strip()

    # 2. Extract Name and Description using stateful regex
    match = re.match(r"(.*?)~(.*?)~", remainder, re.DOTALL)
    if not match:
        raise ValueError(f"Failed to find tilde delimiters in room {vnum}")

    name = match.group(1).strip()
    desc = match.group(2).strip()

    # 3. Process the numeric line that immediately follows the description
    post_desc = remainder[match.end():].strip()
    lines = post_desc.split('\n')
    vector_fields = lines[0].split()
    ```

  - `object.py` fix:

    ```python
           text = text.strip()

        # 1. Extract VNUM safely, ignoring inline builder comments
        match_vnum = re.match(r"^(\d+)(.*)", text, re.DOTALL)
        if not match_vnum:
            raise ValueError("Could not extract VNUM from block")

        obj_id = int(match_vnum.group(1))
        remainder = match_vnum.group(2).strip()

        # 2. Extract the 4 strings using stateful regex, bypassing internal newlines
        match = re.match(r"(.*?)~(.*?)~(.*?)~(.*?)~", remainder, re.DOTALL)
        if not match:
            raise ValueError(f"Failed to find 4 tilde delimiters in object {obj_id}")

        aliases = match.group(1).strip().split()
        short_desc = match.group(2).strip()
        long_desc = match.group(3).strip()
        action_desc = match.group(4).strip() or None

        # 3. Process the remaining numerical and flag lines
        post_desc = remainder[match.end():].strip()
        fields = [line.rstrip() for line in post_desc.split('\n')]
    ```

  - `parser.py` fix:

    ```python
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
    ```

  - `utils.py` fix:
    ```python
        `pattern = re.compile(r'^#(\d+)(?=\s|$|~)', re.MULTILINE)`
        pieces = pattern.split(file_text)
        for vnum, text in zip(pieces[1::2], pieces[2::2]):
            yield vnum + text
    ```
