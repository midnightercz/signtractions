from pytractions.base import Base, TDict, TList

from signtractions.models.signing import LegacySignature


class FakeSigstore(Base):
    """Container reference constructor."""

    base_url: str = ""
    signatures: TDict[str, TDict[str, TList[LegacySignature]]] = TDict[
        str, TDict[str, TList[LegacySignature]]
    ]({})

    def get_signatures(self, image, digest):
        """Get signatures for an image and digest."""
        return self.signatures.get(image, {}).get(digest, [])
