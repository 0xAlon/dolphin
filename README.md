# Dolphin for Home Assistant

[Home Assistant](https://www.home-assistant.io/) Integration for [Dolphin](https://www.dolphinboiler.com) Boiler - Smart Water Heating Control

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

<p align="center"><img src="https://raw.githubusercontent.com/home-assistant/brands/43fe40e19cc76a6d9b18a38bb178f6dcc6ba05d5/custom_integrations/dolphin/logo.png" width="647" height="128" alt=""/></p>

The component is developed by [Alon Teplitsky](https://www.linkedin.com/in/alon-teplitsky/).

## Installation

### HACS

1. Install [HACS](https://hacs.xyz/)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=0xAlon&repository=dolphin&category=integration" target="_blank"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store." /></a>

2. Go to HACS "Integrations >" section
3. In the lower right click "+ Explore & Download repositories"
4. Search for "dolphin" and add it
5. Restart Home Assistant

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=dolphin" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance and start setting up a new integration." /></a>

5. In the Home Assistant UI go to "Settings"
6. Click "Devices & Services"
7. Click "+ Add Integration"
8. Search for "dolphin"

### Manual

1. Using the tool of choice open the directory (folder) for your [HA configuration](https://www.home-assistant.io/docs/configuration/) (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `dolphin`.
4. Download _all_ the files from the `custom_components/dolphin/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the Home Assistant UI go to "Configuration"
8. Click "Integrations"
9. Click "+ Add Integration"
10. Search for "dolphin"

## Devices

A device is created for each dolphin unit. Each device contains:

- `Climate sensor`
- `Electric current sensor`
- `Sabbath mode switch`
- `Shower switches`
