import locations
REGIONS = [
    {
        "prefixe" : "DK",
        "nom" : "DAKAR",
        "climate" : {
            "temp_min" : 25,
            "temp_max" : 38,
            "humidity_min" : 40,
            "humidity_max" : 75,
        },
        "location" : {
            "lat" : locations.regions["Dakar"]["latitude"],
            "lon" : locations.regions["Dakar"]["longitude"]
        }
    },
    {
        "prefixe" : "TH",
        "nom" : "THIES",
        "climate" : {
            "temp_min" : 22,
            "temp_max" : 35,
            "humidity_min" : 35,
            "humidity_max" : 70,
        },
        "location" : {
            "lat" : locations.regions["Thies"]["latitude"],
            "lon" : locations.regions["Thies"]["longitude"]
        }
    },
    {
        "prefixe" : "TB",
        "nom" : "TAMBACOUNDA",
        "climate" : {
            "temp_min" : 20,
            "temp_max" : 45,
            "humidity_min" : 30,
            "humidity_max" : 65,
        },
        "location" : {
            "lat" : locations.regions["Tambacounda"]["latitude"],
            "lon" : locations.regions["Tambacounda"]["longitude"]
        }
    },
    {
        "prefixe" : "MT",
        "nom" : "MATAM",
        "climate" : {
            "temp_min" : 22,
            "temp_max" : 45,
            "humidity_min" : 45,
            "humidity_max" : 60,
        },
        "location" : {
            "lat" : locations.regions["Matam"]["latitude"],
            "lon" : locations.regions["Matam"]["longitude"]
        }
    },
    
]