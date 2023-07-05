import argparse
import logging
from py2neo import Graph, Node, Relationship
# import xml.etree.ElementTree as ET
import lxml.etree as ET
isProduction = False

DEBUG = False

if isProduction:
    INPUT_DB = "data/kanjidic2.xml"
else:
    INPUT_DB = "data/kanjidic2_reduced.xml"

def get_args():
    parser = argparse.ArgumentParser(
                    prog='graphdb_converter',
                    description='Capture Kanji into a Neo4J db'
                    )
    parser.add_argument('--username', dest='username', default="neo4j")
    parser.add_argument('--password', dest='password', default="neo4j")
    parser.add_argument('--port', dest='port', default="7687")
    parser.add_argument('--ip', dest='ip', default="localhost")

    parser.add_argument('--input', dest='inputDB', default=INPUT_DB)

    return parser.parse_args()

def wipe_db(graph):
    cypher_query = "match (a) -[r] -> () delete a, r"
    result = graph.run(cypher_query, value="attribute_value")

    cypher_query = "match (a) delete a"
    result = graph.run(cypher_query, value="attribute_value")
    
def get_node_by_attribute(graph, node_label, node_attr, attr_value):
    # Find the node with a specific attribute value
    cypher_query = f"MATCH (n:{node_label}) WHERE n.{node_attr} = \"{attr_value}\" RETURN n"
    result = graph.run(cypher_query, value="attribute_value").data()

    if result:
        return result[0]['n']
    else:
        print(f"[WARNING] [NODE-NOT-FOUND] {node_label}: {attr_value}.")

    # if result:
    #     # Get the first matching node
    #     node = result[0]['n']
        
    #     # Update the relationship of the node
    #     cypher_query = "MATCH (n)-[r:RELATIONSHIP_TYPE]->() WHERE id(n) = {node_id} SET r.property = {new_value}"
    #     graph.run(cypher_query, node_id=node.identity, new_value="new_property_value")
        
    #     print("Relationship updated successfully.")
    # else:
    #     print("Node not found.")

class Attr():
    def __init__(self, root, path, base_node, attr_key):
        self.root = root
        self.path = path
        self.base_node = base_node
        self.attr_key = attr_key

    def set(self):
        # Add heisig attributes to the kanji node
        elem = self.root.xpath(self.path)

        # if elem is not None:
        if len(elem) > 0:
            self.base_node[self.attr_key] = elem[0].text


def main():
    args = get_args()

    # Connect to Neo4j
    url = f"bolt://{args.ip}:{args.port}"
    graph = Graph(url, user=args.username, password=args.password)

    # Uncomment to cleanup the graph
    #wipe_db(graph)

    # Load the Kanjidic2 XML file
    # tree = ET.parse(args.inputDB)

    # root = tree.getroot()
    root = ET.parse(args.inputDB)

    visited_radicals = []
    visited_grades = []

    # Iterate over the kanji elements
    kanji_elems = root.findall('character')
    for kanji_i, kanji_elem in enumerate(kanji_elems):
        kanji = kanji_elem.find('literal').text
        
        # Create the kanji node with relevant attributes
        kanji_node = Node("Kanji", kanji=kanji)
        
        # Add relevant attributes to the kanji node
        attr_paths = {
            'stroke_count': 'misc/stroke_count',
            'jlpt': 'misc/jlpt',
            'grade': 'misc/grade',
            'heisig': 'dic_number/dic_ref[@dr_type="heisig"]',
            'heisig6': 'dic_number/dic_ref[@dr_type="heisig6"]' 
        }

        for key in attr_paths.keys():
            attr = Attr(root=kanji_elem,
                    path=attr_paths[key],
                    base_node=kanji_node,
                    attr_key=key)

            attr.set()

        rad_nodes, _ = create_node_relation(
            graph=graph,
            root=kanji_elem, path='radical/rad_value[@rad_type="classical"]',
            visited_elems=visited_radicals,
            base_node=kanji_node,
            base_node_text=f"[KANJI] {kanji_node['heisig']}",
            new_node_name="Radical",
            attr_key="rad_name",
            rel_name="HAS_RADICAL")

        rad_val = rad_nodes[0]["rad_name"]
        rad_kanji_path = f"character/reading_meaning/rmgroup/meaning[count(@*)=0][contains(text(),'(no.{rad_val}')]/../../../literal"
        attr = Attr(root=root,
                    path=rad_kanji_path,
                    # path=rad_kanji_path,
                    base_node=rad_nodes[0],
                    attr_key='name')
        attr.set()

        _, _ = create_node_relation(
            graph=graph,
            root=kanji_elem, path='misc/grade',
            visited_elems=visited_grades,
            base_node=kanji_node,
            base_node_text=f"[KANJI] {kanji_node['heisig']}",
            new_node_name="Grade",
            attr_key="grade_name",
            rel_name="HAS_GRADE")

        _, on_rels = create_node_relation(
            graph=graph,
            root=kanji_elem, path='reading_meaning/rmgroup/reading[@r_type="ja_on"]',
            visited_elems=visited_grades,
            base_node=kanji_node,
            base_node_text=f"[KANJI] {kanji_node['heisig']}",
            new_node_name="On",
            attr_key="reading",
            rel_name=None)

        elems = kanji_elem.xpath('reading_meaning/rmgroup/reading[@r_type="ja_on"]')
        for i, elem in enumerate(elems):
            on_rels[i]['readings'] = elem.text

        _, kun_rels = create_node_relation(
            graph=graph,
            root=kanji_elem, path='reading_meaning/rmgroup/reading[@r_type="ja_kun"]',
            visited_elems=visited_grades,
            base_node=kanji_node,
            base_node_text=f"[KANJI] {kanji_node['heisig']}",
            new_node_name="Kun",
            attr_key="reading",
            rel_name=None)

        elems = kanji_elem.xpath('reading_meaning/rmgroup/reading[@r_type="ja_kun"]')
        for i, elem in enumerate(elems):
            if len(kun_rels) > i:
                kun_rels[i]['readings'] = elem.text

        # Add reading.ja_on and reading.ja_kun as attributes to the kanji node
        reading_elems = kanji_elem.findall('reading_meaning/rmgroup/reading[@r_type="ja_on"]')

        kanji_node['ja_on'] = []
        if reading_elems is not None:
            for reading_elem in reading_elems:
                kanji_node['ja_on'].append(reading_elem.text)


        reading_elems = kanji_elem.findall('reading_meaning/rmgroup/reading[@r_type="ja_kun"]')
        if DEBUG:
            if len(reading_elems) > 0:
                t = ""
                for e in reading_elems:
                    t += e.text + "; "
                print("-" + t)
            else:
                print("kanji has no kun")

        kanji_node['ja_kun'] = []
        if reading_elems is not None:
            for reading_e in reading_elems:
                s = reading_e.text.split(".")[0]
                if DEBUG:
                    if s != reading_e.text:
                        print(f"{s} is to be split from {reading_e.text}")
                kanji_node['ja_kun'].append(reading_e.text)

        # Create the kanji node in the graph
        if DEBUG:
            for key in kanji_node.keys():
                print(f"---- {key}: {kanji_node[key]}")

        graph.create(kanji_node)
        # without pushing the list properties won't be updated (kun and on)
        graph.push(kanji_node)

        # only one radical exists for a kanji, but it won't heart to be generic
        for rad_node in rad_nodes:
            graph.push(rad_node)

        for on_rel in on_rels:
            graph.push(on_rel)

        for kun_rel in kun_rels:
            graph.push(kun_rel)

        # Iterate over the variant kanji elements
        for variant_elem in kanji_elem.findall('variant'):
            variant = variant_elem.attrib['var']
            
            # Create the variant kanji node
            variant_node = Node("Kanji", kanji=variant)
            
            # Create a relationship between the kanji and variant kanji nodes
            variant_rel = Relationship(kanji_node, "HAS_VARIANT", variant_node)
            graph.create(variant_rel)

        if kanji_i%50 == 0 and kanji_i > 0:
            print(f"Transformed {kanji_i}/{len(kanji_elems)} kanjis")

def create_node_relation(graph, root, path, base_node, base_node_text, rel_name, new_node_name, attr_key, visited_elems):
    # Create the rad_name node and add rad_value as an attribute
    elems = root.xpath(path)
    new_nodes = []
    rels = []

    if elems is not None:
        for elem in elems:
            new_node = None
            rel = None

            if new_node_name == "Kun":
                attr_val = elem.text.split(".")[0]
            else:
                attr_val = elem.text

            if attr_val in visited_elems:
                logging.debug(base_node_text + f" [OLD-{new_node_name}] {attr_val}")
                new_node = get_node_by_attribute(graph, new_node_name, attr_key, attr_val)
            else:
                logging.debug(base_node_text + f" [NEW-{new_node_name}] {attr_val}")
                new_node = Node(new_node_name)
                new_node[attr_key] = attr_val
                graph.create(new_node)
                visited_elems.append(attr_val)
            
            # Create a relationship between the kanji and rad_name nodes
            if new_node:
                rel = Relationship(base_node, rel_name, new_node)
                graph.create(rel)

            #         # cypher_query = "MATCH (n)-[r:RELATIONSHIP_TYPE]->() WHERE id(n) = {node_id} SET r.property = {new_value}"
            #         # graph.run(cypher_query, node_id=node.identity, new_value="new_property_value")

            if(new_node != None):
                new_nodes.append(new_node)
            if(rel != None):
                rels.append(rel)
            else:
                logging.error(f"{new_node} had no relationship connected to {base_node_text}")

    return new_nodes, rels


def print_kanji(kanji):
    print(kanji.encode("UTF-8"), end='')

if __name__ == "__main__":
    main()
