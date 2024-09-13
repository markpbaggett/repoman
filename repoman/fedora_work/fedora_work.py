from ..fedora_object import FedoraObject
from ..fedora_proxy import FedoraProxy
from rdflib import URIRef, Graph


class FedoraWork(FedoraObject):
    def __init__(self, uri):
        super().__init__(uri)
        self.descriptive_metadata = self.__get_descriptive_metadata()
        self.rights = self.__get_rights()
        self.title = self.__get_title()
        self.summary = self.__get_summary()
        self.members = self.__get_members()
        self.iana_first = list(self.content.objects(
            subject=URIRef(uri), predicate=URIRef(f"{self.namespaces.iana}first")
        ))[0]
        self.iana_last = list(self.content.objects(
            subject=URIRef(uri), predicate=URIRef(f"{self.namespaces.iana}last")
        ))[0]

    def __get_descriptive_metadata(self):
        """Builds a graph with just known descriptive metadata."""
        description = Graph()
        descriptive_predicates = (
            URIRef(f"{self.namespaces.dc}subject"),
            URIRef(f"{self.namespaces.dc}creator"),
            URIRef(f"{self.namespaces.dc}description"),
            URIRef(f"{self.namespaces.dc}format"),
            URIRef(f"{self.namespaces.dc}language"),
            URIRef(f"{self.namespaces.dc}publisher"),
            URIRef(f"{self.namespaces.dc}title"),
            URIRef(f"{self.namespaces.dc}type"),
            URIRef(f"{self.namespaces.dcterms}alternative"),
            URIRef(f"{self.namespaces.dcterms}created"),
            URIRef(f"{self.namespaces.dcterms}extent"),
            URIRef(f"{self.namespaces.dcterms}isPartOf"),
            URIRef(f"{self.namespaces.dcterms}medium"),
        )
        for s, p, o in self.content:
            if p in descriptive_predicates:
                description.add((s, p, o))
        return description

    def __get_rights(self):
        for s, p, o in self.content:
            if p == URIRef(f"{self.namespaces.dc}rights"):
                return str(o)

    def __get_title(self):
        titles = []
        for s, p, o in self.content:
            if p == URIRef(f"{self.namespaces.dc}title"):
                titles.append(str(o.value))
        return titles

    def __get_summary(self):
        for s, p, o in self.content:
            if p == URIRef(f"{self.namespaces.dc}description"):
                return str(o.value)
        return ""

    def __get_members(self):
        return [
            str(o) for s, p, o in self.content if p == URIRef(f"{self.namespaces.pcdm}hasMember")
        ]

    def get_ordered_members(self):
        ordered_members = []
        keep_going = True
        current = FedoraProxy(uri=str(self.iana_first))
        while keep_going:
            ordered_members.append(current.get_proxy_for())
            if current.has_iana_next:
                new_uri = str(current.get_next())
                current = FedoraProxy(uri=new_uri)
            else:
                keep_going = False
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
        for s, p, o in self.descriptive_metadata:
            if p == URIRef(f"{self.namespaces.dc}creator"):
                description['Creator'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dc}subject"):
                description['Subject'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dc}description"):
                description['Description'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dc}language"):
                description['Language'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dc}type"):
                description['Type'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dc}format"):
                description['Format'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dc}publisher"):
                description['Publisher'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dc}type"):
                description['Type'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dcterms}created"):
                description['Date Created'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dcterms}isPartOf"):
                description['Collection'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dcterms}medium"):
                description['Medium'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dcterms}extent"):
                description['Extent'].append(str(o.value))
            elif p == URIRef(f"{self.namespaces.dcterms}alternative"):
                description['Alternative Title'].append(str(o.value))
        return description


if __name__ == '__main__':
    x = FedoraWork(
        'https://api.library.tamu.edu/fcrepo/rest/3b/6f/c3/25/3b6fc325-f6ca-41d8-b91e-8c5db3be8c13/london-collection_objects/11'
    )