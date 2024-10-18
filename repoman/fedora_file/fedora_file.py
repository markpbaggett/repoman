import httpx
from rdflib import URIRef
from repoman.fedora_object import FedoraObject
import os
import base64


class FedoraFile(FedoraObject):
    def __init__(self, uri, position=0):
        super().__init__(uri)
        self.position = position

    def get_files(self):
        return list(self.content.objects(
            subject=URIRef(self.uri), predicate=URIRef(f"{self.namespaces.pcdm}hasFile")
        ))

    def get_contains(self):
        return list(self.content.objects(
            subject=URIRef(self.uri), predicate=URIRef(f"{self.namespaces.ldp}contains")
        ))

    def get_cantaloupe_base_64(self):
        server = self.uri.split('/')[2]
        encoded = base64.urlsafe_b64encode(bytes(self.uri, "utf-8"))
        decoded = encoded.decode("utf-8")
        return f"https://{server}/iiif/2/{decoded}/info.json"

    def download(self, path):
        file_path = str(list(self.content.objects(
            subject=URIRef(self.uri), predicate=URIRef(f"{self.namespaces.pcdm}hasFile")
        ))[0])
        if not os.path.exists(path):
            os.makedirs(path)
        with httpx.Client() as client:
            response = client.get(str(file_path))
            response.raise_for_status()
            with open(f"{path}/{self.position.zfill(4)}_{file_path.split('/')[-1]}", 'wb') as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
