from homeassistant.components.sensor import SensorEntity

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    inventory = hass.data["cannabis_tracker"]["inventory"]
    sensors = []
    for strain in inventory:
        sensors.append(CannabisStrainSensor(strain, hass))
    if sensors:
        add_entities(sensors, True)
    hass.data["entities"] = sensors

class CannabisStrainSensor(SensorEntity):
    def __init__(self, strain_data, hass):
        self._hass = hass
        self._name = strain_data["name"]
        self._type = strain_data.get("type", "Unknown")
        self._quantity = strain_data.get("quantity", 0.0)
        self._purchase_date = strain_data.get("purchase_date", "")
        self._rating = strain_data.get("rating", None)
        self._notes = strain_data.get("notes", "")
        slug = self._name.lower().replace(" ", "_")
        self.entity_id = f"sensor.cannabis_{slug}"

    @property
    def name(self):
        return f"{self._name} (Cannabis)"

    @property
    def native_value(self):
        return self._quantity

    @property
    def native_unit_of_measurement(self):
        return "g"

    @property
    def extra_state_attributes(self):
        return {
            "strain_name": self._name,
            "type": self._type,
            "purchase_date": self._purchase_date,
            "rating": self._rating,
            "notes": self._notes
        }

    @property
    def unique_id(self):
        return f"cannabis_tracker_{self._name.lower().replace(' ', '_')}"

    def update(self):
        for strain in self._hass.data["cannabis_tracker"]["inventory"]:
            if strain["name"] == self._name:
                self._quantity = strain["quantity"]
                self._rating = strain.get("rating", self._rating)
                self._notes = strain.get("notes", self._notes)
                break
