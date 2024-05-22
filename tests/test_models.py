from pytractions.base import TList
from signtractions.models.containers import ContainerParts


def test_container_parts():
    cp = ContainerParts(
        registry="registry",
        image="namespace/repo",
        tag="latest",
        digests=TList[str](["digest"]),
        arches=TList[str](["arch"]),
    )
    cp.make_reference() == "registry/namespace/repo:latest"

    cp = ContainerParts(
        registry="registry",
        image="namespace/repo",
        tag="",
        digests=TList[str](["digest"]),
        arches=TList[str](["arch"]),
    )
    cp.make_reference() == "registry/namespace/repo@digest"
