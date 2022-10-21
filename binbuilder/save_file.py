from versionedobj import VersionedObject


class SavedSchema(VersionedObject):
    version = "1.0"
    schema_data = None
