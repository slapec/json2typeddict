# json2typeddict

This script converts [JSON schema](https://json-schema.org/) into Python source code. The JSON schema is described by [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict).

# Requirements

Python 3.5+

# Usage

    usage: json2typeddict.py [-h] [input_path] [output_path]
    
    Converts JSON schema to Python TypedDict source code
    
    positional arguments:
      input_path   Input .json path. Use - or leave empty for stdin
      output_path  Output .py path. Use - or leave empty for stdout
    
    optional arguments:
      -h, --help   show this help message and exit
      
## Real-life example

Say you're hacking some undocumented JSON APIs and you've already downloaded some json files. Create a JSON schema
from those files using the excellent [genson](https://github.com/wolverdude/genson/) schema generator.

    genson get_users.json > get_users_schema.json
    
Feed the schema into `json2typeddict`

    python json2typeddict.py get_user_schema.json get_user.py
    
In fact, you can pipe the whole thing together

    genson get_users.json | python json2typeddict.py > get_users.py


# State of development

This was one of my friday night projects, so it's not feature complete, but it did the job for me. 

# License

[Do whatever you want with it.](http://www.wtfpl.net/)
