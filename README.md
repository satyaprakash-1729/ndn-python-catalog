# NDN Python Catalog

## The NDN python implementation for NDN catalog (original implementation: NDN Atmos)

Installation:
- git clone https://github.com/satyaprakash-1729/ndn-python-catalog
- cd ndn-python-catalog
- sudo pip3 install -e .

Implement
- Database Adapter Class
- Add Catalog Entry API  -->  Data Name  >>  REPO1, REPO2, REPO3
- Remove Catalog Entry API (Optional)

How to Run?

- ndn-python-catalog --config ndn_python_catalog/ndn-python-catalog.conf --catalog_name 'catalog'

For inserting entries:
	- go into ndn-python-catalog/clients > Run 'python3 insert_client.py'