from signtractions.resources.reference_constructor import (
    ReferenceConstructorInternal,
    ReferenceConstructorExternal,
)


def test_reference_constructor_external():
    """Test ReferenceConstructorExternal."""
    rce = ReferenceConstructorExternal(external_type=1)
    assert rce.construct_reference_tag("registry", "test/repo", "tag") == "registry/test/repo:tag"
    assert (
        rce.construct_reference_digest("registry", "test/repo", "digest")
        == "registry/test/repo@digest"
    )


def test_reference_constructor_internal():
    """Test ReferenceConstructorInternal."""
    rce = ReferenceConstructorInternal(quay_org="quay_org")
    assert (
        rce.construct_reference_tag("registry", "test/repo", "tag")
        == "registry/quay_org/test----repo:tag"
    )
    assert (
        rce.construct_reference_digest("registry", "test/repo", "digest")
        == "registry/quay_org/test----repo@digest"
    )
