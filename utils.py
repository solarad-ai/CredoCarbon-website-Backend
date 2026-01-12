import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import PUBLIC_DATA_DIR


def read_json_file(filename: str) -> dict:
    """Read and parse a JSON file from the public/Data directory."""
    filepath = PUBLIC_DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(filename: str, data: dict) -> None:
    """Write data to a JSON file in the public/Data directory."""
    filepath = PUBLIC_DATA_DIR / filename
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_registry_data() -> dict:
    """Get the current registry data."""
    return read_json_file('registryData.json')


def save_registry_data(data: dict) -> None:
    """Save registry data and update metadata."""
    data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    write_json_file('registryData.json', data)


def get_insights_data() -> dict:
    """Get the current insights data."""
    return read_json_file('insightsData.json')


def save_insights_data(data: dict) -> None:
    """Save insights data and update metadata."""
    data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    write_json_file('insightsData.json', data)


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
