.PHONY: *

deploy:
	rm -rf ./docs/
	cd ./paper/ && mdbook build
	mv ./paper/book/ ./docs/
