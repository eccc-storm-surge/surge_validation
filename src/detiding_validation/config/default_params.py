from collections import OrderedDict

station_dict = OrderedDict([
    ("8443970", "Boston, MA"),
    ("8418150", "Portland, ME"),
    ("8413320", "Bar Harbor, ME"),
    ("8410140", "Eastport, ME"),
    ("65", "Saint John, NB"),
    ("365", "Yarmouth, NS"),
    ("491", "Halifax, NS"),
    ("612", "North Sydney, NS"),
    ("1700", "Charlottetown, PE"),
    ("1805", "Shediac Bay, NB"),
    ("2000", "Lower Escuminac, NB"),
    ("2145", "Belledune, NB"),
    ("2330", "Riviere-au-Renard, QC"),
    ("2985", "Rimouski, QC"),
    ("2780", "Sept-Iles, QC"),
    ("1970", "Cap-aux-Meules, QC"),
    ("665", "Port-aux-Basques, NF"),
    ("755", "St. Lawrence, NF"),
    ("835", "Argentia, NF"),
    ("905", "St Johns, NF"),
    ("990", "Bonavista, NF"),
    ("1430", "Nain, NF"),
])


ignore_in_overall = [491]

vname_to_limits = {
    "stde": (0, 0.1),
    "gamma": (0, 1),
    "stde_obs": (0, 0.1),
    "gamma_varobsallvhour": (0, 1)
}

COLOR_OLD = "b"
COLOR_NEW = "r"
