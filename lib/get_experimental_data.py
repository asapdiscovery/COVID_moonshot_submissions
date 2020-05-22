# Matt Robinson, matthew.robinson@postera.ai
# Compile all experimental info from CDD

# general imports
import numpy as np
import pandas as pd

from rdkit import Chem
from rdkit.Chem import AllChem

import requests
import sys
import time

# get parent path of file
from pathlib import Path

lib_path = Path(__file__).parent.absolute()
with open(lib_path / "CDD.env", "r") as env_file:
    env_vars_dict = dict(
        tuple(line.split("="))
        for line in [x.strip("\n") for x in env_file.readlines()]
        if not line.startswith("#")
    )

vault_num = env_vars_dict["VAULT_num"]
vault_token = env_vars_dict["VAULT_token"]

virtual_project_id = "12336"
synthesis_project_id = "12334"
made_project_id = "12335"

rapidfire_protocol_id = "49700"
fluorescence_protocol_id = "49439"
solubility_protocol_id = "49275"
trypsin_protocol_id = "49443"


def get_rapidfire_data():

    url = f"https://app.collaborativedrug.com/api/v1/vaults/{vault_num}/protocols/{rapidfire_protocol_id}/data?page_size=1000"
    headers = {"X-CDD-token": vault_token}
    response = requests.get(url, headers=headers)
    rapid_fire_dose_response_dict = response.json()["objects"]

    mol_id_list = []
    ic50_list = []

    for mol_dict in rapid_fire_dose_response_dict["objects"]:
        mol_id = mol_dict["molecule"]
        if "560634" in mol_dict["readouts"]:
            ic50 = mol_dict["readouts"]["560634"]
        else:
            ic50 = np.nan

        mol_id_list.append(mol_id)
        ic50_list.append(ic50)

    rapidfire_df = pd.DataFrame(
        {"CDD_mol_ID": mol_id_list, "r_IC50": ic50_list}
    )
    return rapidfire_df


def get_fluorescense_data():

    url = f"https://app.collaborativedrug.com/api/v1/vaults/{vault_num}/protocols/{fluorescence_protocol_id}/data?page_size=1000"
    headers = {"X-CDD-token": vault_token}
    response = requests.get(url, headers=headers)
    fluorescence_response_dict = response.json()["objects"]

    mol_id_list = []
    avg_ic50_list = []
    avg_pic50_list = []
    max_reading_list = []
    min_reading_list = []
    hill_slope_list = []
    r2_list = []

    for mol_dict in fluorescence_response_dict:
        if "molecule" not in mol_dict:
            continue

        elif mol_dict["molecule"] in mol_id_list:
            continue

        mol_id = mol_dict["molecule"]
        if "557736" in mol_dict["readouts"]:
            avg_ic50 = mol_dict["readouts"]["557736"]["value"]
        else:
            avg_ic50 = np.nan

        if "557738" in mol_dict["readouts"]:
            avg_pic50 = mol_dict["readouts"]["557738"]
        else:
            avg_pic50 = np.nan

        if "557085" in mol_dict["readouts"]:
            min_reading = mol_dict["readouts"]["557085"]
        else:
            min_reading = np.nan

        if "557086" in mol_dict["readouts"]:
            max_reading = mol_dict["readouts"]["557086"]
        else:
            max_reading = np.nan

        if "557086" in mol_dict["readouts"]:
            max_reading = mol_dict["readouts"]["557086"]
        else:
            max_reading = np.nan

        if "557078" in mol_dict["readouts"]:
            hill_slope = mol_dict["readouts"]["557078"]
        else:
            hill_slope = np.nan

        if "557082" in mol_dict["readouts"]:
            r2 = mol_dict["readouts"]["557082"]
        else:
            r2 = np.nan

        mol_id_list.append(mol_id)
        avg_ic50_list.append(avg_ic50)
        avg_pic50_list.append(avg_pic50)
        max_reading_list.append(max_reading)
        min_reading_list.append(min_reading)
        hill_slope_list.append(hill_slope)
        r2_list.append(r2)

    fluorescence_df = pd.DataFrame(
        {
            "CDD_mol_ID": mol_id_list,
            "f_avg_IC50": avg_ic50_list,
            "f_avg_pIC50": avg_pic50_list,
            "f_max_inhibition_reading": max_reading_list,
            "f_min_inhibition_reading": min_reading_list,
            "f_hill_slope": hill_slope,
            "f_R2": r2_list,
        }
    )
    return fluorescence_df


def get_solubility_data():

    url = f"https://app.collaborativedrug.com/api/v1/vaults/{vault_num}/protocols/{solubility_protocol_id}/data?page_size=1000"
    headers = {"X-CDD-token": vault_token}
    response = requests.get(url, headers=headers)
    solubility_response_dict = response.json()["objects"]

    solubility_data_dict = {}
    for mol_dict in solubility_response_dict:
        mol_id = mol_dict["molecule"]
        if mol_dict["readouts"]["554984"] == 20.0:
            if mol_id not in solubility_data_dict:
                solubility_data_dict[mol_id] = {
                    "20_uM": mol_dict["readouts"]["555388"]["value"]
                }
            else:
                solubility_data_dict[mol_id]["20_uM"] = mol_dict["readouts"][
                    "555388"
                ]["value"]

        elif mol_dict["readouts"]["554984"] == 100.0:
            if mol_id not in solubility_data_dict:
                solubility_data_dict[mol_id] = {
                    "100_uM": mol_dict["readouts"]["555388"]["value"]
                }
            else:
                solubility_data_dict[mol_id]["100_uM"] = mol_dict["readouts"][
                    "555388"
                ]["value"]

    solubility_data_dict
    mol_id_list = solubility_data_dict.keys()
    relative_solubility_at_20_uM_list = [
        solubility_data_dict[mol_id]["20_uM"] for mol_id in mol_id_list
    ]
    relative_solubility_at_100_uM_list = [
        solubility_data_dict[mol_id]["100_uM"] for mol_id in mol_id_list
    ]

    solubility_df = pd.DataFrame(
        {
            "CDD_mol_ID": mol_id_list,
            "relative_solubility_at_20_uM": relative_solubility_at_20_uM_list,
            "relative_solubility_at_100_uM": relative_solubility_at_100_uM_list,
        }
    )
    return solubility_df


def get_trypsin_data():

    url = f"https://app.collaborativedrug.com/api/v1/vaults/{vault_num}/protocols/{solubility_protocol_id}/data?page_size=1000"
    headers = {"X-CDD-token": vault_token}
    response = requests.get(url, headers=headers)
    trypsin_response_dict = response.json()["objects"]

    mol_id_list = []
    ic50_list = []

    for mol_dict in trypsin_response_dict:
        if "molecule" not in mol_dict:
            continue
        mol_id = mol_dict["molecule"]

        if "557122" in mol_dict["readouts"]:
            if type(mol_dict["readouts"]["557122"]) == float:
                ic50 = mol_dict["readouts"]["557122"]
            else:
                if "value" not in mol_dict["readouts"]["557122"]:
                    ic50 = np.nan
                else:
                    ic50 = mol_dict["readouts"]["557122"]["value"]
        else:
            ic50 = np.nan

        mol_id_list.append(mol_id)
        ic50_list.append(ic50)

    trypsin_df = pd.DataFrame(
        {"CDD_mol_ID": mol_id_list, "trypsin_IC50": ic50_list}
    )
    return trypsin_df
