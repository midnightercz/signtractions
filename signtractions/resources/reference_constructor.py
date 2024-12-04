from pytractions.base import Base


class ReferenceConstructor(Base):
    """Container reference constructor."""

    def construct_reference_digest(self, registry, repo, digest):
        """Construct docker reference for registry repo and digest."""
        pass  # pragma: no cover

    def construct_reference_tag(self, registry, repo, tag):
        """Construct docker reference for registry repo and tag."""


class ReferenceConstructorInternal(ReferenceConstructor):
    """Container reference constructor for repos in internal format."""

    quay_org: str

    def construct_reference_tag(self, registry, repo, tag):
        """Construct docker reference for registry repo and tag."""
        return f"{registry}/{self.quay_org}/{repo.replace('/', '----')}:{tag}"

    def construct_reference_digest(self, registry, repo, digest):
        """Construct docker reference for registry repo and digest."""
        return f"{registry}/{self.quay_org}/{repo.replace('/', '----')}@{digest}"


class ReferenceConstructorExternal(ReferenceConstructor):
    """Container reference constructor for repos in external format."""

    external_type: int

    def construct_reference_tag(self, registry, repo, tag):
        """Construct docker reference for registry repo and tag."""
        return f"{registry}/{repo}:{tag}"

    def construct_reference_digest(self, registry, repo, digest):
        """Construct docker reference for registry repo and digest."""
        return f"{registry}/{repo}@{digest}"
