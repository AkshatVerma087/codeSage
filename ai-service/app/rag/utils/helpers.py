from collections.abc import Iterator

def count_tokens(text: str) -> int:
    return len(text.split())

def dedupe_chunks(chunks: Iterator[dict]) -> list[dict]:
    seen = set()
    result = []
    for chunk in chunks:
        key = (
            chunk.get("file_path"),
            chunk.get("symbol_name"),
            chunk.get("source_code"),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(chunk)
        
    return result

