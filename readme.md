# Midea Air Conditioner via eWeLink Cloud

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/climate_ewelink)](https://github.com/georgezhao2010/climate_ewelink/releases/latest)

English | [简体中文](https://github.com/georgezhao2010/climate_ewelink/blob/main/readme_hans.md)

The custom component of Home Assistant, allows you to control Midea AC devices via the eWeLink cloud.

# Before use

Download the eWeLink App from App Store (iOS) or Google Play (Android), and register a eWeLink account, if you don't already have one.

# Important point about eWeLink account

Compoent may not work with another same ewelink account at the same time (example eWeLink App and Home Assistant or two Home Assistant copies). 
So you need another account, one binds the Midea account and shares devices with the other. 
One account used in Home Assistant and different account used in eWeLink App (or deffrent Home Assistant copy).

# Installtion

Use HACS and Install as a custom repository, or copy all files in `custom_components/cliamte_ewelink` from [Latest Release](https://github.com/georgezhao2010/climate_ewelink/releases/latest) to your `<Home Assistant config folder>/custom_components/cliamte_ewelink` in Home Assistant manually.
Restart HomeAssistant.

# Configuration

Once the integration is installed, go to your integration page and follow the configuration options as below:

- Username (eWeLink App)
- Password (eWeLink App)
- Country (China or Outside China)

# Features

## Climate

- Air conditiner

## Sensor

- Outdoor temperature

## Switches:

- ECO mode
- Comfort mode
- Indirect wind
- Wind swing horizontal
- Wind swing vertical
