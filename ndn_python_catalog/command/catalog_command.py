from ndn.encoding import TlvModel, NameField, RepeatedField, UintField, ModelField


class CatalogCommandParameter(TlvModel):
    """
    Insertion request App Param format.
    """
    name = NameField()


class CatalogResponseParameter(TlvModel):
    """
    Catalog Response App Param format.
    """
    data_name = NameField()
    name = NameField()


class CatalogRequestParameter(TlvModel):
    """
    The data mapping fetch request from a client.
    """
    data_name = NameField()


class CatalogInsertParameter(TlvModel):
    """
    A single Insert Parameter format containing the data name, the name to map and the expiry time.
    """
    data_name = NameField()
    name = NameField()
    expire_time_ms = UintField(8)


class CatalogDeleteParameter(TlvModel):
    """
    A single Delete Parameter format containing the data name and the name mapped to be deleted.
    """
    data_name = NameField()
    name = NameField()


class CatalogDataListParameter(TlvModel):
    """
    The complete insertion request data format. Contains list of insertion and deletion parameters.
    """
    insert_data_names = RepeatedField(ModelField(1, CatalogInsertParameter))
    delete_data_names = RepeatedField(ModelField(2, CatalogDeleteParameter))
