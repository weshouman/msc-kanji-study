
PASSWORD=password

get_source: # get the data
	cd src && \
	if [ ! -f kanjidic2.xml ]; then \
	  wget http://www.edrdg.org/kanjidic/kanjidic2.xml.gz; \
	  gunzip kanjidix2.xml.gz; \
	fi

trex: # Transform tiny example
	cd src && \
	python transformer.py --input-file example.xml \
	                      --output-file example.html \
	                      --type html \
	                      --gen-file example.xslt

trkd: # Transform KanjiDic to a minimal view
	cd src && \
	python transformer.py --input-file kanjidic2.xml \
	                      --output-file kanjidic2.html \
	                      --type html \
	                      --gen-file kanjidic.xslt

trfilter:  # Transform Filter to a reduced dataset
	cd src && \
	python transformer.py --input-file kanjidic2.xml \
	                      --output-file ../data/kanjidic2_reduced.xml \
	                      --type html \
	                      --gen-file kanjidic_filter.xslt

deploy_on_reduced: # deploy a reduced version
	sed -i -e 's#isProduction = .*#isProduction = False#g' src/graphdb_converter.py
	cd src && \
	python graphdb_converter.py --password ${PASSWORD}

deploy: # deploy the full version
	sed -i -e 's#isProduction = .*#isProduction = True#g' src/graphdb_converter.py
	cd src && \
	python graphdb_converter.py --password ${PASSWORD}

vis: # visualize a portion of the graphdb on CLI
	@export NEO4J_URI=neo4j://localhost:7687 && \
  export NEO4J_USERNAME=neo4j && \
	export NEO4J_PASSWORD=${PASSWORD} && \
	cypher-shell -f tests/overview.neo4j

xpath_radicals: # test some xpath
	xmllint --xpath '//character/radical/rad_value[@rad_type="classical"]' ./src/data/kanjidic2_reduced.xml
