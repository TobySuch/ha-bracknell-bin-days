# Bracknell Forest Bin Days for Home Assistant

This Home Assistant integration provides information about bin collection days in Bracknell Forest, UK. It creates 3 sensors for food waste, recycling, and general waste collection days, with the value set to the date of the next collection.

It uses the API endpoint behind the [websites offical page](https://selfservice.mybfc.bracknell-forest.gov.uk/w/webpage/waste-collection-days) to gather this information.

## Installation
1. Make a folder inside your Home Assistant `custom_components` directory called `bracknell_bins`.
2. Copy the contents of this repo into that folder
3. Add the following to your `configuration.yaml` file, replacing `YOUR_ADDRESS_ID` with the address ID for your property (see below for how to find this):
```yaml
sensor:
  - platform: bracknell_bins
    address_id: "YOUR_ADDRESS_ID"
```

## Finding your Address ID
1. Go to the [bin collection days page](https://selfservice.mybfc.bracknell-forest.gov.uk/w/webpage/waste-collection-days) 
2. Open the developer tools in your browser (usually F12 or right-click and select "Inspect").
3. Go to the "Network" tab
4. Enter your postcode and select your address
5. Look for a network request for a POST request to `https://selfservice.mybfc.bracknell-forest.gov.uk/w/webpage/waste-collection-days` and click on it
6. Look under the request data for a form field called `code_params` - the contents will look like the following: `{"addressId":"12345"}`. Copy the number to your configuration.yaml file as your address ID.

## Example Alert Automation
```yaml
alias: Put bins out alert
description: ""
triggers:
  - trigger: time
    at: "20:00:00"
conditions: []
actions:
  - variables:
      bins_due: |
        {% set bins = [
          ('sensor.bin_food', 'Food'),
          ('sensor.bin_recycling', 'Recycling'),
          ('sensor.bin_general_waste', 'General Waste')
        ] %} {% set ns = namespace(due=[]) %} {% for entity, name in bins %}
          {% if state_attr(entity, 'days_until') | int(-1) == 0 %}
            {% set ns.due = ns.due + [name] %}
          {% endif %}
        {% endfor %} {{ ns.due }}
    alias: Calculate bins due tomorrow
  - condition: template
    value_template: "{{ bins_due | length > 0 }}"
    alias: Check if any bins are due tomorrow
  - action: notify.YOUR-DEVICE-HERE
    metadata: {}
    data:
      title: 🗑️ Don't forget to put the bins out!
      message: "Put out: {{ bins_due | join(', ') }}"
mode: single

```