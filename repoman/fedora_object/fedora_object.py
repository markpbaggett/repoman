import httpx
from rdflib import Graph, Namespace


class Namespaces:
    def __init__(self):
        self.dc = "http://purl.org/dc/elements/1.1/"
        self.pcdm = "http://pcdm.org/models#"
        self.iana = "http://www.iana.org/assignments/relation/"
        self.dcterms = "http://purl.org/dc/terms/"
        self.fcrepo = "http://fedora.info/definitions/v4/repository"
        self.rdfs = "http://www.w3.org/1999/02/22-rdf-syntax-ns"
        self.ldp = "http://www.w3.org/ns/ldp#"
        self.ore = "http://www.openarchives.org/ore/terms#"


class FedoraObject:
    def __init__(self, uri):
        self.uri = uri
        self.namespaces = Namespaces()
        self.content = self.__get_graph()

    def __get_graph(self):
        headers = {
            'Accept': 'application/ld+json'
        }
        r = httpx.get(self.uri, headers=headers, timeout=60)
        try:
            if r.status_code == 200:
                g = Graph()
                g.parse(data=r.content, format='json-ld')
                return g
            else:
                raise Exception(f"Failed to download {self.uri}. Status code: {r.status_code}")
        except:
            print(r.status_code)

    def serialize(self, format="turtle"):
        PCDM = Namespace("http://pcdm.org/models#")
        LDP = Namespace("http://www.w3.org/ns/ldp#")
        IANA = Namespace("http://www.iana.org/assignments/relation/")
        FCREPO = Namespace("http://fedora.info/definitions/v4/repository#")
        self.content.bind('pcdm', PCDM)
        self.content.bind('ldp', LDP)
        self.content.bind('iana', IANA)
        self.content.bind('fedora', FCREPO)
        data = self.content.serialize(format=format)
        return data

    def read_graph(self):
        for s, p, o in self.content:
            print(s, p, o)