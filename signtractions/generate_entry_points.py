from .tractors import t_sign_containers
from .tractors import t_sign_repos
from .tractors import t_verifier


from pytractions.pkgutils import traction_entry_points

# Compute the common entry points across all modules

# print("-----")
# for x in traction_entry_points(signtractions.tractors.t_sign_containers):
#     print(x)
# print("-----")

common_entry_points = set()
for ep in traction_entry_points(t_sign_containers):
    common_entry_points.add(ep)
for ep in traction_entry_points(t_sign_repos):
    common_entry_points.add(ep)
# for ep in traction_entry_points(signtractions.tractors.t_sign_snapshot):
#     common_entry_points.add(ep)
for ep in traction_entry_points(t_verifier):
    common_entry_points.add(ep)


print(common_entry_points)
# Write to entry_points.txt
entry_points_file = "signtractions/entry_points.txt"

with open(entry_points_file, "w") as f:
    f.write("[tractions]\n")
    for ep in common_entry_points:
        f.write(f"{ep}\n")

print(f"Generated {entry_points_file}")
