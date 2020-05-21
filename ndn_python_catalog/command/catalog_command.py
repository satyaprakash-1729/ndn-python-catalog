from ndn.encoding import TlvModel, NameField, RepeatedField


class CatalogCommandParameter(TlvModel):
    name = NameField()


class CatalogResponseParameter(TlvModel):
    data_name = NameField()
    name = NameField()


class CatalogRequestParameter(TlvModel):
    data_name = NameField()


class CatalogDataListParameter(TlvModel):
    name = NameField()
    insert_data_names = RepeatedField(NameField())
    delete_data_names = RepeatedField(NameField())
