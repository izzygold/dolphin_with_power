from datetime import timedelta

DOMAIN = "dolphin"
CONF_USERNAME = "Username"
CONF_PASSWORD = "Password"
UPDATE_INTERVAL = timedelta(seconds=30)
PLATFORMS = ["switch", "sensor", "climate"]

# Assumed mains voltage (V) for power/energy derived from reported current (A).
NOMINAL_VOLTAGE_V = 230
