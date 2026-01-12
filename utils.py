import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.cloud import storage
from google.cloud.exceptions import NotFound

from config import (
    PUBLIC_DATA_DIR,
    GCS_BUCKET_NAME,
    GCS_INSIGHTS_FILE,
    GCS_REGISTRY_FILE,
    USE_GCS,
)


# ============ GCS Client Singleton ============

_gcs_client = None


def get_gcs_client():
    """Get or create a GCS client (singleton pattern)."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = storage.Client()
    return _gcs_client


def get_gcs_bucket():
    """Get the GCS bucket."""
    client = get_gcs_client()
    return client.bucket(GCS_BUCKET_NAME)


# ============ GCS Read/Write Functions ============

def read_json_from_gcs(filename: str) -> dict:
    """Read and parse a JSON file from Google Cloud Storage."""
    try:
        bucket = get_gcs_bucket()
        blob = bucket.blob(filename)
        # Reload blob metadata to ensure we get the latest version
        blob.reload()
        content = blob.download_as_text()
        return json.loads(content)
    except NotFound:
        raise FileNotFoundError(f"File not found in GCS: gs://{GCS_BUCKET_NAME}/{filename}")
    except Exception as e:
        raise Exception(f"Error reading from GCS: {str(e)}")


def write_json_to_gcs(filename: str, data: dict) -> None:
    """Write data to a JSON file in Google Cloud Storage."""
    try:
        bucket = get_gcs_bucket()
        blob = bucket.blob(filename)
        content = json.dumps(data, indent=2, ensure_ascii=False)
        # Set cache control to prevent caching issues
        blob.cache_control = 'no-cache, no-store, must-revalidate'
        blob.upload_from_string(content, content_type='application/json')
    except Exception as e:
        raise Exception(f"Error writing to GCS: {str(e)}")


# ============ Local File Read/Write Functions ============

def read_json_file_local(filename: str) -> dict:
    """Read and parse a JSON file from the local public/Data directory."""
    filepath = PUBLIC_DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file_local(filename: str, data: dict) -> None:
    """Write data to a JSON file in the local public/Data directory."""
    filepath = PUBLIC_DATA_DIR / filename
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ============ Unified Read/Write Functions ============

def read_json_file(filename: str) -> dict:
    """Read and parse a JSON file (from GCS or local based on config)."""
    if USE_GCS:
        return read_json_from_gcs(filename)
    else:
        return read_json_file_local(filename)


def write_json_file(filename: str, data: dict) -> None:
    """Write data to a JSON file (to GCS or local based on config)."""
    if USE_GCS:
        write_json_to_gcs(filename, data)
    else:
        write_json_file_local(filename, data)


# ============ Registry Data Functions ============

def get_registry_data() -> dict:
    """Get the current registry data."""
    return read_json_file(GCS_REGISTRY_FILE)


def save_registry_data(data: dict) -> None:
    """Save registry data and update metadata."""
    data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    write_json_file(GCS_REGISTRY_FILE, data)


# ============ Insights Data Functions ============

def get_insights_data() -> dict:
    """Get the current insights data."""
    return read_json_file(GCS_INSIGHTS_FILE)


def save_insights_data(data: dict) -> None:
    """Save insights data and update metadata."""
    data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    write_json_file(GCS_INSIGHTS_FILE, data)


# ============ Helper Functions ============

def calculate_totals(data: dict) -> dict:
    """Recalculate totals based on current registry data."""
    carbon_issued = sum(r.get('issued', 0) or 0 for r in data.get('carbonRegistries', []))
    carbon_retired = sum(r.get('retired', 0) or 0 for r in data.get('carbonRegistries', []))
    
    rec_issued = sum(r.get('issued', 0) or 0 for r in data.get('recRegistries', []))
    rec_retired = sum(r.get('retired', 0) or 0 for r in data.get('recRegistries', []))
    
    # Count unique countries
    all_countries = set()
    for r in data.get('carbonRegistries', []):
        all_countries.add(r.get('country', ''))
    for r in data.get('recRegistries', []):
        all_countries.add(r.get('country', ''))
    for r in data.get('etsRegistries', []):
        all_countries.add(r.get('country', ''))
    all_countries.discard('')
    
    return {
        'carbon': {
            'registries': len(data.get('carbonRegistries', [])),
            'issued': carbon_issued,
            'retired': carbon_retired
        },
        'rec': {
            'registries': len(data.get('recRegistries', [])),
            'issued': rec_issued,
            'retired': rec_retired
        },
        'ets': {
            'registries': len(data.get('etsRegistries', []))
        },
        'totalRegistries': (
            len(data.get('carbonRegistries', [])) + 
            len(data.get('recRegistries', [])) + 
            len(data.get('etsRegistries', []))
        ),
        'totalCountries': len(all_countries)
    }


def update_registry_in_list(registries: list, registry_id: str, updated_data: dict) -> bool:
    """Update a registry in a list by ID. Returns True if found and updated."""
    for i, registry in enumerate(registries):
        if registry.get('id') == registry_id:
            registries[i] = updated_data
            return True
    return False


def add_registry_to_list(registries: list, new_registry: dict) -> None:
    """Add a new registry to a list."""
    registries.append(new_registry)


def delete_registry_from_list(registries: list, registry_id: str) -> bool:
    """Delete a registry from a list by ID. Returns True if found and deleted."""
    for i, registry in enumerate(registries):
        if registry.get('id') == registry_id:
            del registries[i]
            return True
    return False
