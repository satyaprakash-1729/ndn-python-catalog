from ndn.encoding import TlvModel, NameField, RepeatedField, UintField, ModelField


class CatalogCommandParameter(TlvModel):
    name = NameField()


class CatalogResponseParameter(TlvModel):
    data_name = NameField()
    name = NameField()


class CatalogRequestParameter(TlvModel):
    data_name = NameField()


class CatalogInsertParameter(TlvModel):
    data_name = NameField()
    name = NameField()
    expire_time_ms = UintField(8)


class CatalogDeleteParameter(TlvModel):
    data_name = NameField()
    name = NameField()


class CatalogDataListParameter(TlvModel):
    insert_data_names = RepeatedField(ModelField(1, CatalogInsertParameter))
    delete_data_names = RepeatedField(ModelField(2, CatalogDeleteParameter))
