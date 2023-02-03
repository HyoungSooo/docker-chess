def write_pgn_chunk_files(value, version, name):
    with open(f"{version}_{name}", 'wb+') as f:
        f.write(value)
    f.close()
