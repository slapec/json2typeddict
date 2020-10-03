# coding: utf-8

import argparse
import collections
import json
import sys
from typing import List


JSON_TO_PY_TYPES = {
    'string': 'str',
    'integer': 'int',
    'null': 'Optional[Any]',
    'number': 'float',
    'boolean': 'bool',
    ('array', 'null'): 'Union[List[Any], Optional[Any]]'
}


parser = argparse.ArgumentParser(
    description='Converts JSON schema to Python TypedDict source code'
)

parser.add_argument(
    'input_path',
    help='Input .json path. Use - or leave empty for stdin',
    nargs='?',
    type=argparse.FileType('r'),
    default=sys.stdin
)


parser.add_argument(
    'output_path',
    help='Output .py path. Use - or leave empty for stdout',
    nargs='?',
    type=argparse.FileType('w'),
    default=sys.stdout
)


class Annotation:
    def __init__(self):
        self._annotations = []

    def add(self, annotation):
        self._annotations.append(annotation)

    def __str__(self):
        if len(self._annotations) > 1:
            return 'Union[' + ', '.join(self._annotations) + ']'
        else:
            return self._annotations[0]

    def __repr__(self):
        return str(self)


class ClassDescription:
    def __init__(self, name):
        self.class_name = name
        self.annotations = collections.defaultdict(Annotation)

    def __repr__(self):
        return '<{0}({1})>'.format(self.class_name, self.annotations)


def json2typeddict(schema):
    class_description_list = []  # type: List[ClassDescription]

    def walk(json_node, class_name='ResponseDict', parent_property=None, parent_py_node=None):
        node_type = json_node.get('type', None)
        if isinstance(node_type, list):
            node_type = tuple(sorted(node_type))

        any_of = json_node.get('anyOf', None)

        if node_type == 'object':
            py_node = ClassDescription(class_name)
            class_description_list.insert(0, py_node)
            for property_name, property_node in json_node['properties'].items():
                # I know underscores in class names are not PEP8 but it's just much easier to read generated code
                walk(property_node, class_name + '_' + property_name, property_name, py_node)

        elif node_type == 'array':
            items = json_node.get('items', None)
            if items:
                subtype = items['type']
                python_type = JSON_TO_PY_TYPES.get(subtype, None)
                if python_type:
                    parent_py_node.annotations[parent_property].add('List[{0}]'.format(python_type))
                else:
                    parent_py_node.annotations[parent_property].add('List[{0}]'.format(class_name))
                    walk(items, class_name, parent_property, parent_py_node)
            else:
                parent_py_node.annotations[parent_property].add('List[Any]')

        else:
            if any_of:
                for i, subnode in enumerate(any_of):
                    walk(subnode, class_name + '_' + str(i), parent_property, parent_py_node)

            else:
                python_type = JSON_TO_PY_TYPES[node_type]
                parent_py_node.annotations[parent_property].add(python_type)

    walk(schema)

    return class_description_list


if __name__ == '__main__':
    args = parser.parse_args()

    with args.input_path as f:
        schema = json.load(f)

    description_list = json2typeddict(schema)

    with args.output_path as f:
        def out(s):
            return print(s, file=f)

        for node in description_list:
            out('class {0}(TypedDict):'.format(node.class_name))
            for key, value in sorted(node.annotations.items()):
                out('    {0}: {1}'.format(key, value))
            out('\n')
