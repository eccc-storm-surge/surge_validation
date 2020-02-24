from collections import OrderedDict
import numpy as np

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
    ("2246", "Saint-Pierre, FR"),
    ("1040", "Carmanville, NL"),
    ("1098", "Springdale, NL"),
    ("1170", "St. Anthony, NL"),
    ("1186", "Henley Harbour, NL"),
    ("1630", "Pictou, NS"),
    ("1915", "Rustico, PE"),
    ("2375", "Southwest Point, QC"),
    ("2550", "Harrington Harbour, QC"),
    ("880", "Trepassey, NL"),
    ("325", "Digby, NS"),
    ("475", "Mill Cove, NS"),
    ("576", "Point Tupper, NS"),
    ("2590", "Forteau, NL"),
    ("2633", "Savage Cove, NL"),
    ("2685", "Lark Harbour, NL"),
    ("2840", "Baie-Comeau, QC"),
    ("2935", "Ste-Anne-des-Monts, QC"),
    ("550", "Sable Island, NS"),
    ("900", "Bay Bulls, NL"),
    ("1050", "Fogo, NL"),
    ("1680", "Wood Islands, PE"),

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


score_clevs = {
    "gamma2": np.arange(0, 0.6, 0.05),
    "sigma": np.arange(0, 0.2, 0.02),
    "gamma2_diff": np.arange(-0.20, 0.21, 0.02),
    "sigma_diff": np.arange(-0.06, 0.07, 0.02),

}
