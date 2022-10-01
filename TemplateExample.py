from PyPE.Template import Template, TemplateFn
from textwrap import dedent
import sys

@TemplateFn
def writeAstring():
    writeAstring.context.write("This is from the TemplateFn")

src = r"""
    Text should be added as is
    @[ if name == "fred":
          write("The write function is availabe in Templates\n")
          write(name)
          write("\nNewlines must be added explicitly with write")
    ]@
    
    Variables can be created on the fly. For the block below, unindent
    the if statement above and set a few variables. Remove the return value
    at the end of this below so that no empty line shows up in the rendered
    text.
    @[: a = "testing"
        bob = 5
        q=7
      ^]@
    Values can be written out. Remove the newline at the start of the block
    below: 
    @[^= bob  ]@
    # The size of a code block can be preserved
    # 
    @[^>"make this string right aligned. "^]@
    Remove the newline at the start and end.
    
    @[writeAstring()]@
    """
src = dedent(src)

# This template will be created from a string rather than read from a file, so
# set readFile to False and call addPythonFunction with the template src above.
t = Template("Temp", readFile=False)
t.addPythonFunction(src)
t.addTemplateFunctions(sys.modules[__name__])     # Load TemplateFn from this file
print(t.render({'name':"fred", 'a':"A Value"}))
