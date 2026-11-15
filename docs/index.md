---
title: Home
nav_order: 1
---

# GeniusHub (alternate) integration for Home Assistant

The **Genius Hub** integration links Home Assistant with your Genius Hub CH/DHW system, including its zones, devices, and issues.

It uses the [geniushub](https://pypi.org/project/geniushub-client/) client library, which provides data compatible with the v1 API that _may not_ exactly match that of the official Web App.

## Prerequisites

You can configure the integration either via the cloud API or the local API.

- **Cloud API**: requires a **hub token** obtained from [my.geniushub.co.uk](https://my.geniushub.co.uk/).
- **Local API**: requires your **username** and **password** as used with [geniushub.co.uk/app](https://www.geniushub.co.uk/).

The local API is unofficial, but is faster and has more features, while the cloud API is slower.

# Installation
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=RogerSelwyn&repository=GeniusHub)

You can either use Marketplace or install the component manually:
- **Marketplace** - search for and install GeniusHub Alt

- **Manual** - Put the files from `/custom_components/geniushub_alt/` in your folder `<config directory>/custom_components/geniushub_alt/`

## Configuration
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=geniushub_alt)

<details markdown="1"><summary>Manual configuration</summary>
  
If the above My button doesn't work, you can also perform the following steps manually: 
* Browse to your Home Assistant instance.
* Go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations). 
* In the bottom right corner, select the [Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=geniushub_alt) button.
* From the list, select GeniusHub Alt.
* Follow the instructions on screen to complete the setup.
  
</details>


## Removing the integration

This integration follows standard integration removal. Remember to remove via Marketplace as well.

### To remove an integration instance from Home Assistant

1. Go to [**Settings** > **Devices & services**](https://my.home-assistant.io/redirect/integrations) and select the integration card.
2. From the list of devices, select the integration instance you want to remove.
3. Next to the entry, select the three-dot menu. Then, select **Delete**.



