# signtractions

## What is signtractions

Signtractions project is set of pytraction tractions, tractors, models and resources which wraps functionality of pubtools-sign project to provide
containerized container singing.

## How to use signtractions

### Locally
1. Install signtractions on your local machine
2. Run following python command to excute tractor or traction from signtractions
```
cat run_arguments.yml | python -m pytractions.cli run signtractions.<path-to-traction/tractor-you-want-to-run>:<Traction-or-Tractor-Class>
```

### In Container
2. Run following python command to excute tractor or traction from signtractions in a container
```
cat run_arguments.yml | podman -v userdata:/userdata run -i signtractions:latest run signtractions.<path-to-traction/tractor-you-want-to-run>:<Traction-or-Tractor-Class>
```

### Tekton task
1. To generate tekton Task spec you can run
```
podman signtractions:latest generate_tekton_task signtractions.<path-to-traction/tractor-you-want-to-run>:<Traction-or-Tractor-Class> quay.io/jluza/signtractions:latest
```
2. To generate tekton TaskRun spec you can run
```
podman signtractions:latest generate_tekton_task_run signtractions.<path-to-traction/tractor-you-want-to-run>:<Traction-or-Tractor-Class> quay.io/jluza/signtractions:latest
```

3. To generate pipeline instead of task, you just pass `--type tractor` after `'generate_tekton_task_run'`. Only tractors can be generated as tekton pipelines


### Generating default inputs
1. To generate yaml file with default inputs used to feed running tractor or tractions (run_arguments.yml in examples above) you can run
```
python -m pytractions.cli generate_inputs signtractions.<path-to-traction/tractor-you-want-to-run>:<Traction-or-Tractor-Class>
```
or
```
podman signtractions:latest generate_inputs signtractions.<path-to-traction/tractor-you-want-to-run>:<Traction-or-Tractor-Class>
```


#### More info about pytractions
More info about framework used to build this project can be found here:
https://github.com/midnightercz/pytractions/
Or by running
```
podman run -p 8501:8501 signtractions:latest web
```
 
---
##Generated part

## Available tractions in this project
### Distribution: signtractions

---
---

### Distribution: pytractions

**Name**: pytractions.transformations:Extractor

**Docs**: 

**Inputs**:
* **Name**: i_model

	**Type**: In[T]

	**Docs**: 


**Outputs**:
* **Name**: o_model

	**Type**: Out[X]

	**Docs**: 


**Resources**:


**Args**:
* **Name**: a_field

	**Type**: Arg[str]

	**Docs**: 

---
**Name**: pytractions.transformations:FilterDuplicates

**Docs**: 

**Inputs**:
* **Name**: i_list

	**Type**: In[TList[T]]

	**Docs**: 


**Outputs**:
* **Name**: o_list

	**Type**: Out[TList[T]]

	**Docs**: 


**Resources**:


**Args**:

---
**Name**: pytractions.transformations:Flatten

**Docs**: 

**Inputs**:
* **Name**: i_complex

	**Type**: In[TList[TList[T]]]

	**Docs**: 


**Outputs**:
* **Name**: o_flat

	**Type**: Out[TList[T]]

	**Docs**: 


**Resources**:


**Args**:

---
**Name**: pytractions.transformations:ListMultiplier

**Docs**: Takes lengh of input list and creates output list of the same length filled
with scalar value.

**Inputs**:
* **Name**: i_list

	**Type**: In[TList[T]]

	**Docs**: Input list.
	

* **Name**: i_scalar

	**Type**: In[X]

	**Docs**: Scalar value.


**Outputs**:
* **Name**: o_list

	**Type**: Out[TList[X]]

	**Docs**: Output list.


**Resources**:


**Args**:

---
---



## Available tractors in this project
### Distribution: signtractions

**Name**: signtractions.tractors.t_sign_containers:SignContainers

**Docs**: 
    Sign container images provided as input in cosign wrapper with signing keys provided as input.


**Inputs**:
* **Name**: i_container_image_references

	**Type**: In[TList[str]]

	**Docs**: List of container image references to sign.
	

* **Name**: i_task_id

	**Type**: In[int]

	**Docs**: Task ID to identify signing request.
	

* **Name**: i_signing_keys

	**Type**: In[TList[str]]

	**Docs**: List of signing keys used to sign containers. One key per container.


**Outputs**:
* **Name**: o_sign_entries

	**Type**: Out[TList[SignEntry]]

	**Docs**: 


**Resources**:
* **Name**: r_signer_wrapper_cosign

	**Type**: Res[Union[MsgSignerWrapper,CosignSignerWrapper]]

	**Docs**: 
	

* **Name**: r_dst_quay_client

	**Type**: Res[QuayClient]

	**Docs**: 


**Args**:
* **Name**: a_pool_size

	**Type**: Arg[int]

	**Docs**: Pool size used for STMD tractions
	

* **Name**: a_executor_type

	**Type**: Arg[STMDExecutorType]

	**Docs**: 

---
---

### Distribution: pytractions

---
---

