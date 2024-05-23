import string
from pytractions.catalog import catalog, _type_to_str

def make_str(tractions):
    tractions_str = []
    for traction in tractions:
        traction_str = []
        traction_str.append("**Name**: " + traction['module'] + ':' +  traction['name'] + "\n")
        traction_str.append("**Docs**: " + (traction['docs'] or "") + "\n")
        inputs = []
        for input_ in traction['inputs']:
            input_str = []
            input_str.append("* **Name**: " + input_['name'] + "\n")
            input_str.append("\t**Type**: " + _type_to_str(input_['type']) + "\n")
            input_str.append("\t**Docs**: " + (input_['docs'] or "") + "\n")
            inputs.append("\n".join(input_str))
        inputs_str = "\t\n\n".join(inputs)
        traction_str.append("**Inputs**:\n" + inputs_str + "\n")

        outputs = []
        for output_ in traction['outputs']:
            output_str = []
            output_str.append("* **Name**: " + output_['name'] + "\n")
            output_str.append("\t**Type**: " + _type_to_str(output_['type']) + "\n")
            output_str.append("\t**Docs**: " + (output_['docs'] or "") + "\n")
            outputs.append("\n".join(output_str))
        outputs_str = "\t\n\n".join(outputs)
        traction_str.append("**Outputs**:\n" + outputs_str + "\n")

        resources = []
        for res in traction['resources']:
            resource_str = []
            resource_str.append("* **Name**: " + res['name'] + "\n")
            resource_str.append("\t**Type**: " + _type_to_str(res['type']) + "\n")
            resource_str.append("\t**Docs**: " + (res['docs'] or "") + "\n")
            resources.append("\n".join(resource_str))
        resources_str = "\t\n\n".join(resources)
        traction_str.append("**Resources**:\n" + resources_str + "\n")
    
        args = []
        for arg in traction['args']:
            arg_str = []
            arg_str.append("* **Name**: " + arg['name'] + "\n")
            arg_str.append("\t**Type**: " + _type_to_str(arg['type']) + "\n")
            arg_str.append("\t**Docs**: " + (arg['docs'] or "") + "\n")
            args.append("\n".join(arg_str))
        args_str = "\t\n\n".join(args)
        traction_str.append("**Args**:\n" + args_str + "\n")
        traction_str = "\n".join(traction_str)
        tractions_str.append(traction_str)
    return "---\n".join(tractions_str)


t = string.Template(open("README.in").read())
distributions = []
_distributions = catalog(type_filter="TRACTION")[0]
for d in _distributions:
    dist = "### Distribution: " + d['name'] + '\n\n' + make_str(d['tractions'])
    dist += "---\n---\n"
    distributions.append(dist)
tractions_list = "\n".join(distributions)

distributions = []
_distributions = catalog(type_filter="TRACTOR")[0]
for d in _distributions:
    dist = "### Distribution: " + d['name'] + '\n\n' + make_str(d['tractions'])
    dist += "---\n---\n"
    distributions.append(dist)
tractors_list = "\n".join(distributions)

with open("README.md", "w") as f:
    f.write(t.substitute(TRACTIONS_LIST=tractions_list, TRACTORS_LIST=tractors_list))
