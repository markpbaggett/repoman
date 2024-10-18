from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import URIRef, Graph, Literal

class FusekiQuery:
    def __init__(self, sparql_endpoint):
        self.sparql_endpoint = SPARQLWrapper(sparql_endpoint)

    def get_predicates_and_objects(self, subject=None, return_graph=False):
        if subject is None:
            s = "?s"
        else:
            s = f"<{subject}>"
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ebucore: <http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#>
        SELECT ?p ?o  WHERE {{
            {s} ?p ?o .
        }} 
        """
        self.sparql_endpoint.setQuery(query)
        self.sparql_endpoint.setReturnFormat(JSON)
        results = self.sparql_endpoint.query().convert()
        if return_graph:
            return self.__build_graph(
                subject,
                results["results"]["bindings"]
            )
        return results["results"]["bindings"]

    def __build_graph(self, subject, results):
        final = Graph()
        for result in results:
            object_type = result['o']['type']
            if object_type == 'uri':
                object_value = URIRef(result['o']['value'])
            elif object_type == 'literal':
                object_value = Literal(result['o']['value'])
            final.add((URIRef(subject), URIRef(result['p']['value']), object_value))
        return final.serialize(format="turtle", indent=4)


if __name__ == "__main__":
    x = FusekiQuery(sparql_endpoint="https://api.library.tamu.edu/fcrepo-fuseki/fcrepo/query")
    print(
        x.get_predicates_and_objects(
            "https://api.library.tamu.edu/fcrepo/rest/3b/6f/c3/25/3b6fc325-f6ca-41d8-b91e-8c5db3be8c13/BasbanesEternalPassion_objects/13",
            return_graph=True
        )
    )