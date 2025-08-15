# signtractions

## What is signtractions

Signtractions project is set of pytraction tractions, tractors, models and resources which wraps functionality of pubtools-sign project to provide
containerized container singing.

## How to use signtractions

### Web UI

Pull signtractions container image from quay.io
```
podman pull quay.io/jluza/signtractions:<version>
```
and run it with
```
podman run -u userdata:/userdata -p 4200:4200 quay.io/jluza/signtractions:<version>
```
In user userdata directory you can place client certificates and other files needed for various tractors.
Then run `localhost:4200` in your web browser and follow the instructions.
NOTE: It takes some time to start the web UI, so be patient.


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
### Distribution: pytractions

**Name**: pytractions.transformations:Extractor

**Docs**: 

**Inputs**:
* **Name**: i_model

	**Type**: Port[T]

	**Docs**: 


**Outputs**:
* **Name**: o_model

	**Type**: Port[X]

	**Docs**: 


**Resources**:


**Args**:
* **Name**: a_field

	**Type**: Port[str]

	**Docs**: 

---
**Name**: pytractions.transformations:FilterDuplicates

**Docs**: 

**Inputs**:
* **Name**: i_list

	**Type**: Port[TList[T]]

	**Docs**: 


**Outputs**:
* **Name**: o_list

	**Type**: Port[TList[T]]

	**Docs**: 


**Resources**:


**Args**:

---
**Name**: pytractions.transformations:Flatten

**Docs**: 

**Inputs**:
* **Name**: i_complex

	**Type**: Port[TList[TList[T]]]

	**Docs**: 


**Outputs**:
* **Name**: o_flat

	**Type**: Port[TList[T]]

	**Docs**: 


**Resources**:


**Args**:

---
**Name**: pytractions.transformations:ListMultiplier

**Docs**: Takes lengh of input list and creates output list of the same length filled
with scalar value.

**Inputs**:
* **Name**: i_list

	**Type**: Port[TList[T]]

	**Docs**: Input list.
	

* **Name**: i_scalar

	**Type**: Port[X]

	**Docs**: Scalar value.


**Outputs**:
* **Name**: o_list

	**Type**: Port[TList[X]]

	**Docs**: Output list.


**Resources**:


**Args**:

---
---

### Distribution: signtractions

**Name**: signtractions.tractors.t_sign_containers:ChunkSignEntries

**Docs**: Chunk provided SignEntries into chunks.

**Inputs**:
* **Name**: i_sign_entries

	**Type**: Port[TList[SignEntry]]

	**Docs**: List of SignEntry objects to chunk.
	

* **Name**: i_chunk_size

	**Type**: Port[int]

	**Docs**: Size of each chunk.


**Outputs**:
* **Name**: o_chunked_sign_entries

	**Type**: Port[TList[TList[SignEntry]]]

	**Docs**: List of chunked SignEntry objects.


**Resources**:


**Args**:

---
**Name**: signtractions.tractions.snapshot:ContainerImagesFromSnapshot

**Docs**: Extract container image references from SnapshotSpec object.

**Inputs**:
* **Name**: i_snapshot_spec

	**Type**: Port[SnapshotSpec]

	**Docs**: SnapshotSpec object


**Outputs**:
* **Name**: o_container_images

	**Type**: Port[TList[str]]

	**Docs**: List of container image references
	

* **Name**: o_container_identities

	**Type**: Port[TList[str]]

	**Docs**: List of container identities


**Resources**:


**Args**:

---
**Name**: signtractions.tractors.t_verifier:Evaluate

**Docs**: Evaluate availability of found signatures.
Results are stored in Google Sheets where each column represent a container image identity and sigstore (cosign or legacy)
and ever row represent a timestamp of the evaluation. Values of each availability cells are either positive integers (found)
or negative integers (not found).




**Inputs**:
* **Name**: i_sign_entries

	**Type**: Port[TList[SignEntry]]

	**Docs**: Sign entries which ever verified.
	

* **Name**: i_found_signatures_legacy

	**Type**: Port[TDict[SignEntry,bool]]

	**Docs**: Signatures found in legacy sigstore.
	

* **Name**: i_found_signatures_cosign

	**Type**: Port[TDict[SignEntry,bool]]

	**Docs**: Signatures found in cosign.


**Outputs**:


**Resources**:
* **Name**: r_gsheets

	**Type**: Port[GSheets]

	**Docs**: Google Sheets resource.


**Args**:

---
**Name**: pytractions.transformations:Flatten

**Docs**: 

**Inputs**:
* **Name**: i_complex

	**Type**: Port[TList[TList[T]]]

	**Docs**: 


**Outputs**:
* **Name**: o_flat

	**Type**: Port[TList[T]]

	**Docs**: 


**Resources**:


**Args**:

---
**Name**: pytractions.transformations:ListMultiplier

**Docs**: Takes lengh of input list and creates output list of the same length filled
with scalar value.

**Inputs**:
* **Name**: i_list

	**Type**: Port[TList[T]]

	**Docs**: Input list.
	

* **Name**: i_scalar

	**Type**: Port[X]

	**Docs**: Scalar value.


**Outputs**:
* **Name**: o_list

	**Type**: Port[TList[X]]

	**Docs**: Output list.


**Resources**:


**Args**:

---
**Name**: signtractions.tractions.snapshot:ParseSnapshot

**Docs**: Parse snapshot json string into SnapshotSpec 
object (https://pkg.go.dev/github.com/redhat-appstudio/rhtap-cli/api/v1alpha1#SnapshotSpec)

**Inputs**:
* **Name**: i_snapshot_str

	**Type**: Port[str]

	**Docs**: Snapshot string in json format
	

* **Name**: i_snapshot_file

	**Type**: Port[str]

	**Docs**: Snapshot file path


**Outputs**:
* **Name**: o_snapshot_spec

	**Type**: Port[SnapshotSpec]

	**Docs**: Parsed Snapshot object (json format)


**Resources**:


**Args**:

---
**Name**: signtractions.tractions.verify:VerifyEntriesCosign

**Docs**: Verify SignEntries have signatures in the cosign sigstore.

**Inputs**:
* **Name**: i_sign_entries

	**Type**: Port[TList[SignEntry]]

	**Docs**: List of SignEntries to verify
	

* **Name**: i_public_key_file

	**Type**: Port[str]

	**Docs**: Public key file


**Outputs**:
* **Name**: o_verified

	**Type**: Port[TDict[SignEntry,bool]]

	**Docs**: Dictionary of SignEntry to verification status


**Resources**:


**Args**:

---
**Name**: signtractions.tractions.verify:VerifyEntriesLegacy

**Docs**: Verify SignEntries have signatures in the legacy sigstore.

**Inputs**:
* **Name**: i_sign_entries

	**Type**: Port[TList[SignEntry]]

	**Docs**: List of SignEntries to verify


**Outputs**:
* **Name**: o_verified

	**Type**: Port[TDict[SignEntry,bool]]

	**Docs**: Dictionary of SignEntry to verification status


**Resources**:
* **Name**: r_sigstore

	**Type**: Port[Union[Sigstore,FakeSigstore]]

	**Docs**: Sigstore resource


**Args**:

---
---



## Available tractors in this project
### Distribution: pytractions

---
---

### Distribution: signtractions

**Name**: signtractions.tractors.t_sign_containers:SignContainers

**Docs**: 
    Sign container images provided as input in cosign wrapper with signing keys provided as input.


**Inputs**:
* **Name**: i_container_image_references

	**Type**: Port[TList[str]]

	**Docs**: List of container image references to sign.
	

* **Name**: i_container_image_identities

	**Type**: Port[TList[str]]

	**Docs**: List of container image identities.
	

* **Name**: i_task_id

	**Type**: Port[int]

	**Docs**: Task ID to identify signing request.
	

* **Name**: i_signing_keys

	**Type**: Port[TList[str]]

	**Docs**: List of signing keys used to sign containers. One key per container.
	

* **Name**: i_chunk_size

	**Type**: Port[int]

	**Docs**: Size of each chunk used to split sign entries to chunks for parallel signing.


**Outputs**:
* **Name**: o_sign_entries

	**Type**: Port[TList[SignEntry]]

	**Docs**: List of SignEntry objects signed.


**Resources**:
* **Name**: r_signer_wrapper_cosign

	**Type**: Port[Union[FakeCosignSignerWrapper,MsgSignerWrapper,CosignSignerWrapper]]

	**Docs**: Signer wrapper used to sign container images with cosign.
	

* **Name**: r_dst_quay_client

	**Type**: Port[Union[QuayClient,FakeQuayClient]]

	**Docs**: 


**Args**:
* **Name**: a_executor

	**Type**: Port[Union[ProcessPoolExecutor,ThreadPoolExecutor,LoopExecutor]]

	**Docs**: Executor used for parallel processing.
	

* **Name**: a_dry_run

	**Type**: Port[bool]

	**Docs**: Dry run flag to simulate signing without actual signing.

---
**Name**: signtractions.tractors.t_sign_snapshot:SignSnapshot

**Docs**: 
    Sign containers in release snapshot.


**Inputs**:
* **Name**: i_snapshot_str

	**Type**: Port[str]

	**Docs**: Json representation of release snapshot.
	

* **Name**: i_snapshot_file

	**Type**: Port[str]

	**Docs**: Path to a file containing snapshot in json format.
	

* **Name**: i_signing_key

	**Type**: Port[str]

	**Docs**: Signing key used to sign containers. One key per container.
	

* **Name**: i_chunk_size

	**Type**: Port[int]

	**Docs**: Chunk size for parallel processing.
	

* **Name**: i_task_id

	**Type**: Port[int]

	**Docs**: Task ID to identify signing request.


**Outputs**:
* **Name**: o_sign_entries

	**Type**: Port[TList[SignEntry]]

	**Docs**: List of SignEntry objects representing signed containers.


**Resources**:
* **Name**: r_signer_wrapper_cosign

	**Type**: Port[Union[FakeCosignSignerWrapper,MsgSignerWrapper,CosignSignerWrapper]]

	**Docs**: Signer wrapper used to sign container images.
	

* **Name**: r_dst_quay_client

	**Type**: Port[Union[QuayClient,FakeQuayClient]]

	**Docs**: Quay client used for fetching container images when populating digests in SignEntries.


**Args**:
* **Name**: a_executor

	**Type**: Port[Union[ProcessPoolExecutor,ThreadPoolExecutor,LoopExecutor]]

	**Docs**: Executor used for parallel processing.

---
**Name**: signtractions.tractors.t_verifier:Verifier

**Docs**: 

**Inputs**:
* **Name**: i_container_image_references

	**Type**: Port[TList[str]]

	**Docs**: Container image identities to verify.
	

* **Name**: i_container_image_identities

	**Type**: Port[TList[str]]

	**Docs**: 
	

* **Name**: i_public_key_file

	**Type**: Port[str]

	**Docs**: Public key file to verify cosign signatures.
	

* **Name**: i_signing_keys

	**Type**: Port[TList[str]]

	**Docs**: Signing key used to populate SignEntry models.
For this tractor they do no need to make sense.


**Outputs**:


**Resources**:
* **Name**: r_signer_wrapper_cosign

	**Type**: Port[Union[FakeCosignSignerWrapper,MsgSignerWrapper,CosignSignerWrapper]]

	**Docs**: Cosign signer wrapper.
	

* **Name**: r_dst_quay_client

	**Type**: Port[Union[QuayClient,FakeQuayClient]]

	**Docs**: Destination Quay client.
	

* **Name**: r_sigstore

	**Type**: Port[Union[Sigstore,FakeSigstore]]

	**Docs**: Sigstore client.
	

* **Name**: r_gsheets

	**Type**: Port[Union[GSheets,FakeGSheets]]

	**Docs**: Google Sheets client.


**Args**:
* **Name**: a_executor

	**Type**: Port[Union[ProcessPoolExecutor,ThreadPoolExecutor,LoopExecutor]]

	**Docs**: Executor to use.
	

* **Name**: a_dry_run

	**Type**: Port[bool]

	**Docs**: Dry run mode.

---
---

