# Docs
This is documentation files of sphinx, along with the generated docs as HTML.

THERE IS NO NEED TO RUN IT AS AN END USER, this code is meant for maintainers of the project to generate and update the documentation. Although, it is possible to view the documentation offline by opening the `./build/index.html` file.

## Generation: How to run
make sure you are in the ./docs directory, NOT in ./docs/source
first generate autodoc/apidoc files based on source python files.
```
$ sphinx-apidoc -o ./source/autodoc ../../src/EIMTC/plugins
```

and then generate docs by:
```
$ make html
```

