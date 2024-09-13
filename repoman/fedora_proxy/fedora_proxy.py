from repoman import FedoraObject
from rdflib import URIRef


class FedoraProxy(FedoraObject):
    def __init__(self, uri):
        super().__init__(uri)
        self.proxy_for = list(self.content.objects(
            subject=URIRef(uri), predicate=URIRef(f"{self.namespaces.ore}proxyFor")
        ))
        self.iana_next = list(self.content.objects(
            subject=URIRef(uri), predicate=URIRef(f"{self.namespaces.iana}next")
        ))
        self.has_proxy_for = self.check_exists(self.proxy_for)
        self.has_iana_next = self.check_exists(self.iana_next)

    @staticmethod
    def check_exists(value):
        return len(value) > 0

    def get_next(self):
        return str(self.iana_next[0]) if self.iana_next else None

    def get_proxy_for(self):
        return str(self.proxy_for[0]) if self.proxy_for else None