# Power Dolphin for Home Assistant

[Home Assistant](https://www.home-assistant.io/) integration for [Dolphin](https://www.dolphinboiler.com) smart water heaters, published as **`power_dolphin`** (domain and folder name) so it can live beside the upstream **`dolphin`** integration if needed.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

<p align="center"><img src="https://raw.githubusercontent.com/home-assistant/brands/43fe40e19cc76a6d9b18a38bb178f6dcc6ba05d5/custom_integrations/dolphin/logo.png" width="647" height="128" alt=""/></p>

---

## This repository is a fork

**We did not create the original integration.** This repo is a **fork** that adds **power** and **energy** sensors on top of an existing, working project.

The integration was originally developed by **[Alon Teplitsky](https://www.linkedin.com/in/alon-teplitsky/)** ([@0xAlon](https://github.com/0xAlon) on GitHub). Alon’s work is what makes Dolphin boilers talk to Home Assistant in the first place, and it does that job well. We have no interest in replacing that project or suggesting there is anything “wrong” with it—this fork exists only because we wanted extra entities for our own homes.

**Upstream (baseline) repository:** [github.com/0xAlon/dolphin](https://github.com/0xAlon/dolphin)

If you do not need calculated power or energy, you may prefer to stay on Alon’s repository; it is the natural home for the core integration and broader community discussion.

### Why we forked

On supported devices, the upstream integration exposes **electric current in amperes (A)**. We also wanted:

- **Electric power (W)** — for live load and automations.
- **Electric energy (kWh)** — for long-term use and the Home Assistant **Energy** dashboard.

The data path used by the integration does not provide separate voltage or energy readings from the device, so this fork **computes** them:

- **Power:** \(P \approx 230\,\mathrm{V} \times I\) (fixed nominal voltage; change `NOMINAL_VOLTAGE_V` in `custom_components/power_dolphin/const.py` if your supply differs).
- **Energy:** kWh accumulated between coordinator updates from that power (trapezoidal rule over time), with the total **restored after a Home Assistant restart**.

Those assumptions are approximations (real mains voltage and power factor vary). They are good enough for many monitoring and Energy-dashboard use cases; treat the numbers accordingly.

### Integration id: `power_dolphin`

This fork installs as **`power_dolphin`** (not `dolphin`). Entity ids use the `power_dolphin.*` prefix. If you previously used a build named `dolphin`, remove the old integration entry and add **Power Dolphin** again, or keep both integrations only if you intentionally want two connections (not typical).

---

## Installation

Use **this** repository (`izzygold/dolphin_with_power`), not the HACS default search result for “dolphin”, unless you intentionally want the upstream integration without these sensors.

### HACS (recommended)

1. Install [HACS](https://hacs.xyz/) if you have not already.
2. In Home Assistant, open **HACS** → **Integrations**.
3. Open the menu (⋮) → **Custom repositories**.
4. Add repository **`https://github.com/izzygold/dolphin_with_power`**, category **Integration**, then **Add**.
5. In **HACS** → **Integrations**, open **+ Explore & download repositories**, find **Power Dolphin** (or **power_dolphin**) from this custom repo, and **Download**.
6. Restart Home Assistant.

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=izzygold&repository=dolphin_with_power&category=integration" target="_blank"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open this fork’s repository in HACS." /></a>

7. In Home Assistant go to **Settings** → **Devices & services** → **+ Add integration** → search for **Power Dolphin** or **`power_dolphin`** and complete the config flow (password is entered in a masked field).

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=power_dolphin" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance and start setting up the Power Dolphin integration." /></a>

### Manual

1. Open your [Home Assistant configuration folder](https://www.home-assistant.io/docs/configuration/) (where `configuration.yaml` lives).
2. If there is no `custom_components` folder, create it.
3. Inside `custom_components`, create a folder named **`power_dolphin`**.
4. Copy **all** files from the `custom_components/power_dolphin/` directory **of this repository** into that `power_dolphin` folder (not from the upstream repo, if you want power/energy).
5. Restart Home Assistant.
6. Go to **Settings** → **Devices & services** → **+ Add integration** → search for **Power Dolphin** / **`power_dolphin`**.

---

## Devices

For each Dolphin unit, Home Assistant gets a device with (among other entities):

- Climate / water heater controls (as in upstream)
- **Electric current (A)** — from the boiler, on supported hardware
- **Electric power (W)** — calculated from current and nominal 230 V (this fork)
- **Electric energy (kWh)** — integrated over time for Energy dashboard–friendly totals (this fork)
- Fixed temperature, Sabbath mode, and shower switches (as in upstream)

---

## Credits

- **Original integration:** [Alon Teplitsky](https://www.linkedin.com/in/alon-teplitsky/) / [@0xAlon](https://github.com/0xAlon) — [0xAlon/dolphin](https://github.com/0xAlon/dolphin).
- **This fork:** power/energy sensors, `power_dolphin` domain, and documentation updates for [izzygold/dolphin_with_power](https://github.com/izzygold/dolphin_with_power).

If you hit bugs that are specific to **power, energy, or the 230 V assumption**, open an issue on **this** repository. For core Dolphin/API behaviour shared with upstream, consider checking upstream issues too—fixes there help everyone.
