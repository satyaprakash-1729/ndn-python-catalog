from ndn.encoding import TlvModel, NameField


class CatalogCommandParameter(TlvModel):
    data_name = NameField()
    repo_name = NameField()


class CatalogResponseParameter(TlvModel):
    data_name = NameField()
    repo_name = NameField()
