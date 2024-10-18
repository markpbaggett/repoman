from ..fedora_object import FedoraObject
from ..fedora_proxy import FedoraProxy
from rdflib import URIRef, Graph


class FedoraWork(FedoraObject):
    def __init__(self, uri):
        super().__init__(uri)
        self.uri = URIRef(uri)
        self.descriptive_metadata = self.__get_descriptive_metadata()
        self._cache = {}
        self.iana_first = self.__get_iana('first')
        self.iana_last = self.__get_iana('last')

    def __get_iana(self, name):
        return next(self.content.objects(subject=self.uri, predicate=URIRef(f"{self.namespaces.iana}{name}")), None)

    def __get_descriptive_metadata(self):
        """Builds a graph with just known descriptive metadata."""
        description = Graph()
        descriptive_predicates = {
            f"{self.namespaces.dc}subject",
            f"{self.namespaces.dc}creator",
            f"{self.namespaces.dc}description",
            f"{self.namespaces.dc}format",
            f"{self.namespaces.dc}language",
            f"{self.namespaces.dc}publisher",
            f"{self.namespaces.dc}title",
            f"{self.namespaces.dc}type",
            f"{self.namespaces.dcterms}alternative",
            f"{self.namespaces.dcterms}created",
            f"{self.namespaces.dcterms}extent",
            f"{self.namespaces.dcterms}isPartOf",
            f"{self.namespaces.dcterms}medium",
        }
        for s, p, o in self.content:
            if str(p) in descriptive_predicates:
                description.add((s, p, o))
        return description

    def __get_cached(self, key, func):
        """Helper to cache expensive operations."""
        if key not in self._cache:
            self._cache[key] = func()
        return self._cache[key]

    @property
    def rights(self):
        return self.__get_cached('rights', lambda: self.__get_first_literal(f"{self.namespaces.dc}rights"))

    @property
    def title(self):
        return self.__get_cached('title', lambda: self.__get_all_literals(f"{self.namespaces.dc}title"))

    @property
    def summary(self):
        return self.__get_cached('summary', lambda: self.__get_first_literal(f"{self.namespaces.dc}description"))

    @property
    def members(self):
        return self.__get_cached('members', lambda: self.__get_all_objects(f"{self.namespaces.pcdm}hasMember"))

    def __get_first_literal(self, predicate):
        for _, p, o in self.content:
            if str(p) == predicate:
                return str(o)
        return ""

    def __get_all_literals(self, predicate):
        return [str(o) for _, p, o in self.content if str(p) == predicate]

    def __get_all_objects(self, predicate):
        return [str(o) for _, p, o in self.content if str(p) == predicate]

    def get_ordered_members(self):
        ordered_members = []
        current = FedoraProxy(uri=str(self.iana_first))
        while current:
            ordered_members.append(current.get_proxy_for())
            if current.has_iana_next:
                current = FedoraProxy(uri=str(current.get_next()))
            else:
                current = None
        return ordered_members

    def metadata_to_dict(self):
        description = {
            "Alternative Title": [],
            "Date Created": [],
            "Subject": [],
            "Creator": [],
            "Publisher": [],
            "Collection": [],
            "Format": [],
            "Type": [],
            "Medium": [],
            "Description": [],
            "Language": [],
            "Extent": []
        }

        predicates_map = {
            "Creator": f"{self.namespaces.dc}creator",
            "Subject": f"{self.namespaces.dc}subject",
            "Description": f"{self.namespaces.dc}description",
            "Language": f"{self.namespaces.dc}language",
            "Type": f"{self.namespaces.dc}type",
            "Format": f"{self.namespaces.dc}format",
            "Publisher": f"{self.namespaces.dc}publisher",
            "Date Created": f"{self.namespaces.dcterms}created",
            "Collection": f"{self.namespaces.dcterms}isPartOf",
            "Medium": f"{self.namespaces.dcterms}medium",
            "Extent": f"{self.namespaces.dcterms}extent",
            "Alternative Title": f"{self.namespaces.dcterms}alternative"
        }

        for s, p, o in self.descriptive_metadata:
            for key, pred in predicates_map.items():
                if str(p) == pred:
                    description[key].append(str(o))

        return description


if __name__ == '__main__':
    x = FedoraWork(
        'https://api.library.tamu.edu/fcrepo/rest/3b/6f/c3/25/3b6fc325-f6ca-41d8-b91e-8c5db3be8c13/london-collection_objects/9'
    )

