import hashlib
import json


def canonicalize_payload(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_event_hash(previous_hash: str, payload: dict) -> tuple[str, str]:
    payload_hash = compute_sha256(canonicalize_payload(payload))
    event_hash = compute_sha256(previous_hash + payload_hash)
    return payload_hash, event_hash
