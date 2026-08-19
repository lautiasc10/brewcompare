(function () {
  "use strict";
  window.__DB__ = {
  "site": {
    "name": "BrewCompare",
    "currency": "USD",
    "store": "Amazon.com",
    "affiliate_tag": "YOURTAG-20"
  },
  "categories": [
    {
      "id": "home",
      "name": "Home",
      "tagline": "One or two coffee drinkers, a normal kitchen counter.",
      "blurb": "Machines built for a household: simple menus, easy daily cleaning and a price that makes sense against a daily café habit."
    },
    {
      "id": "office",
      "name": "Office",
      "tagline": "Shared kitchens, several people, all day long.",
      "blurb": "Bigger hoppers, multiple user profiles and milk systems that survive being used by people who will not read the manual."
    },
    {
      "id": "professional",
      "name": "Professional",
      "tagline": "High volume, back-to-back drinks.",
      "blurb": "Machines with the thermal recovery and duty cycle to keep going through a rush without a cool-down."
    },
    {
      "id": "premium",
      "name": "Premium",
      "tagline": "The best cup money can buy at home.",
      "blurb": "Top-tier extraction technology, colour displays, one-touch specialities and the build to match the price tag."
    }
  ],
  "specGroups": [
    {
      "id": "extraction",
      "name": "Extraction & brewing"
    },
    {
      "id": "grinder",
      "name": "Grinder"
    },
    {
      "id": "capacity",
      "name": "Capacities"
    },
    {
      "id": "drinks",
      "name": "Drinks & controls"
    },
    {
      "id": "milk",
      "name": "Milk system"
    },
    {
      "id": "care",
      "name": "Cleaning & maintenance"
    },
    {
      "id": "physical",
      "name": "Build & dimensions"
    }
  ],
  "specs": [
    {
      "key": "pressure_bar",
      "label": "Pump pressure",
      "group": "extraction",
      "type": "number",
      "unit": "bar",
      "better": "higher",
      "compare": true
    },
    {
      "key": "power_w",
      "label": "Power",
      "group": "extraction",
      "type": "number",
      "unit": "W",
      "better": "none",
      "compare": true
    },
    {
      "key": "boiler_type",
      "label": "Heating system",
      "group": "extraction",
      "type": "text",
      "unit": null,
      "better": "none",
      "compare": true
    },
    {
      "key": "first_cup_seconds",
      "label": "First cup from cold",
      "group": "extraction",
      "type": "number",
      "unit": "s",
      "better": "lower",
      "compare": true
    },
    {
      "key": "temperature_settings",
      "label": "Brew temperature levels",
      "group": "extraction",
      "type": "number",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "grinder_integrated",
      "label": "Integrated grinder",
      "group": "grinder",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "grinder_type",
      "label": "Burr type",
      "group": "grinder",
      "type": "text",
      "unit": null,
      "better": "none",
      "compare": true
    },
    {
      "key": "grind_settings",
      "label": "Grind settings",
      "group": "grinder",
      "type": "number",
      "unit": "steps",
      "better": "higher",
      "compare": true
    },
    {
      "key": "bypass_doser",
      "label": "Pre-ground bypass",
      "group": "grinder",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "water_tank_l",
      "label": "Water tank",
      "group": "capacity",
      "type": "number",
      "unit": "L",
      "better": "higher",
      "compare": true
    },
    {
      "key": "bean_hopper_g",
      "label": "Bean hopper",
      "group": "capacity",
      "type": "number",
      "unit": "g",
      "better": "higher",
      "compare": true
    },
    {
      "key": "grounds_capacity",
      "label": "Grounds drawer",
      "group": "capacity",
      "type": "number",
      "unit": "pucks",
      "better": "higher",
      "compare": true
    },
    {
      "key": "drinks_one_touch",
      "label": "One-touch drinks",
      "group": "drinks",
      "type": "number",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "user_profiles",
      "label": "User profiles",
      "group": "drinks",
      "type": "number",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "display_type",
      "label": "Display",
      "group": "drinks",
      "type": "text",
      "unit": null,
      "better": "none",
      "compare": true
    },
    {
      "key": "touchscreen",
      "label": "Touch controls",
      "group": "drinks",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "iced_coffee_mode",
      "label": "Iced coffee mode",
      "group": "drinks",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "milk_system",
      "label": "Milk system",
      "group": "milk",
      "type": "text",
      "unit": null,
      "better": "none",
      "compare": true
    },
    {
      "key": "milk_one_touch",
      "label": "One-touch milk drinks",
      "group": "milk",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "milk_carafe_l",
      "label": "Milk carafe",
      "group": "milk",
      "type": "number",
      "unit": "L",
      "better": "higher",
      "compare": true
    },
    {
      "key": "auto_rinse",
      "label": "Automatic rinse cycle",
      "group": "care",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "auto_milk_clean",
      "label": "Automatic milk cleaning",
      "group": "care",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "removable_brew_group",
      "label": "Removable brew group",
      "group": "care",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "water_filter",
      "label": "Water filter system",
      "group": "care",
      "type": "text",
      "unit": null,
      "better": "none",
      "compare": true
    },
    {
      "key": "dishwasher_safe_parts",
      "label": "Dishwasher-safe parts",
      "group": "care",
      "type": "bool",
      "unit": null,
      "better": "higher",
      "compare": true
    },
    {
      "key": "noise_db",
      "label": "Grinder noise",
      "group": "physical",
      "type": "number",
      "unit": "dB",
      "better": "lower",
      "compare": true
    },
    {
      "key": "housing_material",
      "label": "Housing material",
      "group": "physical",
      "type": "text",
      "unit": null,
      "better": "none",
      "compare": true
    },
    {
      "key": "width_cm",
      "label": "Width",
      "group": "physical",
      "type": "number",
      "unit": "cm",
      "better": "lower",
      "compare": true
    },
    {
      "key": "depth_cm",
      "label": "Depth",
      "group": "physical",
      "type": "number",
      "unit": "cm",
      "better": "lower",
      "compare": true
    },
    {
      "key": "height_cm",
      "label": "Height",
      "group": "physical",
      "type": "number",
      "unit": "cm",
      "better": "lower",
      "compare": true
    },
    {
      "key": "weight_kg",
      "label": "Weight",
      "group": "physical",
      "type": "number",
      "unit": "kg",
      "better": "none",
      "compare": true
    },
    {
      "key": "warranty_years",
      "label": "Warranty",
      "group": "physical",
      "type": "number",
      "unit": "yr",
      "better": "higher",
      "compare": true
    }
  ],
  "scores": [
    {
      "key": "coffee",
      "label": "Coffee quality",
      "how": "Pump pressure, burr type and grind range, extraction technology (pulse / pre-infusion) and the temperature control on offer."
    },
    {
      "key": "milk",
      "label": "Milk drinks",
      "how": "Whether milk drinks are one-touch, how good the foam is in hands-on reviews, and how forgiving the system is for a beginner."
    },
    {
      "key": "ease",
      "label": "Ease of use",
      "how": "Display quality, number of one-touch recipes, user profiles, and how much you have to learn before the first good cup."
    },
    {
      "key": "care",
      "label": "Cleaning",
      "how": "Removable brew group, automatic rinse and milk-clean cycles, dishwasher-safe parts and how long descaling intervals are."
    },
    {
      "key": "quiet",
      "label": "Quietness",
      "how": "Measured grinder noise where reviewers published a figure, plus consistent reports of noise in owner reviews."
    },
    {
      "key": "value",
      "label": "Value",
      "how": "What you get per dollar against the rest of this catalogue, at the price the machine actually sells for."
    }
  ],
  "series": [
    "var(--s1)",
    "var(--s2)",
    "var(--s3)",
    "var(--s4)"
  ],
  "products": [
    {
      "id": "delonghi-magnifica-evo",
      "name": "De'Longhi Magnifica Evo ECAM29043SB",
      "shortName": "Magnifica Evo",
      "brand": "De'Longhi",
      "model": "ECAM29043SB",
      "url": "machine-delonghi-magnifica-evo.html",
      "image": "assets/img/delonghi-magnifica-evo-1.svg",
      "images": [
        "assets/img/delonghi-magnifica-evo-1.svg",
        "assets/img/delonghi-magnifica-evo-2.svg",
        "assets/img/delonghi-magnifica-evo-3.svg"
      ],
      "affiliateUrl": "https://www.amazon.com/dp/B0B38KFWNK?tag=YOURTAG-20",
      "retailPrice": 749.95,
      "salePrice": 599.95,
      "price": 599.95,
      "priceDate": "2026-08-19",
      "rating": 4.4,
      "ratingCount": 38,
      "categories": [
        "home"
      ],
      "badge": "Best value",
      "summary": "The cheapest way into real bean-to-cup espresso without giving up a proper burr grinder. You get 15-bar extraction, 13 grind settings and a removable brew group at a price where most machines still use a pressurised basket. The catch is the milk: it is a manual steam wand, so lattes are a skill you learn rather than a button you press.",
      "specs": {
        "pressure_bar": 15,
        "power_w": 1250,
        "boiler_type": "Thermoblock",
        "first_cup_seconds": 38,
        "temperature_settings": 3,
        "grinder_integrated": true,
        "grinder_type": "Steel conical burr",
        "grind_settings": 13,
        "bypass_doser": true,
        "water_tank_l": 1.8,
        "bean_hopper_g": 250,
        "grounds_capacity": 14,
        "drinks_one_touch": 7,
        "user_profiles": 1,
        "display_type": "Backlit soft-touch panel",
        "touchscreen": true,
        "iced_coffee_mode": true,
        "milk_system": "Manual steam wand",
        "milk_one_touch": false,
        "milk_carafe_l": null,
        "auto_rinse": true,
        "auto_milk_clean": false,
        "removable_brew_group": true,
        "water_filter": "De'Longhi water softener filter",
        "dishwasher_safe_parts": true,
        "noise_db": 68,
        "housing_material": "Plastic with stainless steel internals",
        "width_cm": 24.0,
        "depth_cm": 44.0,
        "height_cm": 36.0,
        "weight_kg": 9.4,
        "warranty_years": 2
      },
      "scores": {
        "coffee": 7,
        "milk": 5,
        "ease": 7,
        "care": 8,
        "quiet": 5,
        "value": 9
      },
      "avgScore": 6.8
    },
    {
      "id": "philips-5400-lattego",
      "name": "Philips 5400 Series LatteGo EP5447/94",
      "shortName": "Philips 5400 LatteGo",
      "brand": "Philips",
      "model": "EP5447/94",
      "url": "machine-philips-5400-lattego.html",
      "image": "assets/img/philips-5400-lattego-1.svg",
      "images": [
        "assets/img/philips-5400-lattego-1.svg",
        "assets/img/philips-5400-lattego-2.svg",
        "assets/img/philips-5400-lattego-3.svg"
      ],
      "affiliateUrl": "https://www.amazon.com/dp/B092NGG9NM?tag=YOURTAG-20",
      "retailPrice": 1099.0,
      "salePrice": 799.0,
      "price": 799.0,
      "priceDate": "2026-08-19",
      "rating": 4.89,
      "ratingCount": 142,
      "categories": [
        "office",
        "home"
      ],
      "badge": "Easiest to live with",
      "summary": "The machine that asks the least of you. Twelve one-touch drinks, four user profiles plus a guest slot, and a milk carafe with no tubes that rinses under the tap in about fifteen seconds. It is the obvious pick for a shared kitchen, and the only real complaint is that the grinder is loud.",
      "specs": {
        "pressure_bar": 15,
        "power_w": 1500,
        "boiler_type": "Thermoblock",
        "first_cup_seconds": null,
        "temperature_settings": 3,
        "grinder_integrated": true,
        "grinder_type": "100% ceramic burr",
        "grind_settings": 12,
        "bypass_doser": true,
        "water_tank_l": 1.8,
        "bean_hopper_g": 275,
        "grounds_capacity": 12,
        "drinks_one_touch": 12,
        "user_profiles": 5,
        "display_type": "Colour TFT",
        "touchscreen": true,
        "iced_coffee_mode": false,
        "milk_system": "LatteGo two-piece tube-free carafe",
        "milk_one_touch": true,
        "milk_carafe_l": 0.26,
        "auto_rinse": true,
        "auto_milk_clean": true,
        "removable_brew_group": true,
        "water_filter": "AquaClean CA6903",
        "dishwasher_safe_parts": true,
        "noise_db": 79,
        "housing_material": "Plastic with chrome finish",
        "width_cm": 24.6,
        "depth_cm": 43.3,
        "height_cm": 37.2,
        "weight_kg": 8.0,
        "warranty_years": 2
      },
      "scores": {
        "coffee": 7,
        "milk": 8,
        "ease": 9,
        "care": 9,
        "quiet": 3,
        "value": 8
      },
      "avgScore": 7.3
    },
    {
      "id": "jura-e8",
      "name": "Jura E8 Automatic Coffee Machine (Piano Black)",
      "shortName": "Jura E8",
      "brand": "Jura",
      "model": "E8 / EA 15270",
      "url": "machine-jura-e8.html",
      "image": "assets/img/jura-e8-1.svg",
      "images": [
        "assets/img/jura-e8-1.svg",
        "assets/img/jura-e8-2.svg",
        "assets/img/jura-e8-3.svg"
      ],
      "affiliateUrl": "https://www.amazon.com/dp/B097S6RL3T?tag=YOURTAG-20",
      "retailPrice": 2599.0,
      "salePrice": 2299.0,
      "price": 2299.0,
      "priceDate": "2026-08-19",
      "rating": 3.9,
      "ratingCount": 91,
      "categories": [
        "premium",
        "office",
        "professional"
      ],
      "badge": "Best cup",
      "summary": "The best cup in this catalogue, from the machine that asks the highest price for it. Pulse Extraction genuinely improves short drinks, the 3.5-inch colour display makes seventeen specialities easy to navigate, and everything cleans itself. The brew group is sealed, though, and owner reviews are noticeably more mixed than the marketing suggests.",
      "specs": {
        "pressure_bar": 15,
        "power_w": 1450,
        "boiler_type": "Thermoblock with Pulse Extraction Process",
        "first_cup_seconds": null,
        "temperature_settings": 3,
        "grinder_integrated": true,
        "grinder_type": "Professional Aroma Grinder, stainless conical burr",
        "grind_settings": 6,
        "bypass_doser": true,
        "water_tank_l": 1.9,
        "bean_hopper_g": 280,
        "grounds_capacity": 16,
        "drinks_one_touch": 17,
        "user_profiles": 1,
        "display_type": "3.5\" colour TFT",
        "touchscreen": true,
        "iced_coffee_mode": false,
        "milk_system": "Automatic frother with fine-foam technology",
        "milk_one_touch": true,
        "milk_carafe_l": null,
        "auto_rinse": true,
        "auto_milk_clean": true,
        "removable_brew_group": false,
        "water_filter": "CLARIS Smart+",
        "dishwasher_safe_parts": true,
        "noise_db": null,
        "housing_material": "Plastic with chrome accents",
        "width_cm": 27.0,
        "depth_cm": 44.7,
        "height_cm": 34.8,
        "weight_kg": 10.2,
        "warranty_years": 2
      },
      "scores": {
        "coffee": 9,
        "milk": 8,
        "ease": 9,
        "care": 7,
        "quiet": 7,
        "value": 5
      },
      "avgScore": 7.5
    }
  ]
};
})();
