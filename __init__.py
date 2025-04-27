import json
import os
from homeassistant.helpers import discovery

DOMAIN = "cannabis_tracker"
DATA_FILE = "cannabis_inventory.json"  # file in HA config dir

async def async_setup(hass, config):
    """Set up the cannabis tracker integration."""
    data_path = hass.config.path(DATA_FILE)
    inventory = []
    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            inventory = json.load(f)
    else:
        with open(data_path, "w") as f:
            json.dump([], f)

    hass.data[DOMAIN] = {"inventory": inventory, "data_path": data_path}

    def save_inventory():
        with open(data_path, "w") as f:
            json.dump(hass.data[DOMAIN]["inventory"], f, indent=2)

    async def handle_add_strain(call):
        name = call.data.get("name")
        strain_type = call.data.get("type", "Unknown")
        quantity = call.data.get("quantity", 0.0)
        purchase_date = call.data.get("purchase_date", "")
        rating = call.data.get("rating", None)
        notes = call.data.get("notes", "")
        if not name:
            return
        new_strain = {
            "name": name,
            "type": strain_type,
            "quantity": quantity,
            "purchase_date": purchase_date,
            "rating": rating,
            "notes": notes
        }
        hass.data[DOMAIN]["inventory"].append(new_strain)
        save_inventory()
        hass.async_create_task(discovery.async_load_platform(
            hass, "sensor", DOMAIN, {}, config
        ))

    async def handle_update_strain(call):
        name = call.data.get("name")
        if not name:
            return
        for strain in hass.data[DOMAIN]["inventory"]:
            if strain["name"].lower() == name.lower():
                if "quantity" in call.data:
                    strain["quantity"] = call.data["quantity"]
                if "rating" in call.data:
                    strain["rating"] = call.data["rating"]
                if "notes" in call.data:
                    strain["notes"] = call.data["notes"]
                break
        save_inventory()
        for entity in hass.data.get("entities", []):
            entity.async_write_ha_state()

    hass.services.async_register(DOMAIN, "add_strain", handle_add_strain)
    hass.services.async_register(DOMAIN, "update_strain", handle_update_strain)

    hass.async_create_task(discovery.async_load_platform(
        hass, "sensor", DOMAIN, {}, config
    ))

    return True
