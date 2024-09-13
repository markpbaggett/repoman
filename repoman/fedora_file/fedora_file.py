import httpx
from rdflib import URIRef
from repoman.fedora_object import FedoraObject


class FedoraFile(FedoraObject):
    def __init__(self, uri, position):
        super().__init__(uri)
        self.position = position

    def download(self, path):
        file_path = str(list(self.content.objects(
            subject=URIRef(self.uri), predicate=URIRef(f"{self.namespaces.pcdm}hasFile")
        ))[0])
        with httpx.Client() as client:
            response = client.get(str(file_path))
            response.raise_for_status()
            with open(f"{path}/{self.position.zfill(4)}_{file_path.split('/')[-1]}", 'wb') as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
