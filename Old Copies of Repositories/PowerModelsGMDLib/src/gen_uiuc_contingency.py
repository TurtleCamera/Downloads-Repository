# %% Scale br_v by a factor of 15
import json, os
from pathlib import Path

# %%
mods_rel_path = "data/uiuc-150-bus-system/pti/uiuc-150bus_mods.json"
mods_path = os.path.join(Path.home(), 'Repos', 'PowerModelsGMDLib', mods_rel_path)
mods_path

# %%
with open(mods_path) as f:
    net = json.load(f)

# %%

for g in net['gmd_branch'].values():
    g['br_v'] *= 15.0

# %%
contingency_rel_path = "data/uiuc-150-bus-system/pti/uiuc-150bus_15kvm_contingency_mods.json"
contingency_path = os.path.join(Path.home(), 'Repos', 'PowerModelsGMDLib', contingency_rel_path)
contingency_path

# %% 
with open(contingency_path, 'w') as f:
    json.dump(net, f, indent=4)