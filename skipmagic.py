import re
import sys
from io import StringIO

from IPython.core.display import HTML, display

skip_traceback = True

ipython = get_ipython()

reaesc = re.compile(r"\x1b[^m]*m")


ausgabehtml1 = """
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 18px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .collapsible:hover {
  background-color: #555;
}

.collapsible:after {
  content: '+'; /* \02795Unicode character for "plus" sign (+) */
  font-size: 15px;
  color: white;
  float: right;
  margin-left: 5px;

  margin-right: 15px;

}

.active:after {
  content: "-"; /* \2796Unicode character for "minus" sign (-) */
}
.content {
  padding: 0 18px;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.2s ease-out;
  background-color: #f1f1f1;
}
</style>
</head>
<body>

<button class="collapsible">"""

ausgabehtml2 = """</button>
<div class="content">
  <p>"""

ausgabehtml3 = """</p>
</div>


<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    } 
  });
}
</script>

</body>
</html>"""


def hide_traceback(
    exc_tuple=None,
    filename=None,
    tb_offset=None,
    exception_only=False,
    running_compiled_code=False,
):
    etype, value, tb = sys.exc_info()

    syntaxflag = False
    if issubclass(etype, SyntaxError):
        syntaxflag = True

    if syntaxflag == False:

        # if errors
        x = "???"
        for i in ipython.InteractiveTB.structured_traceback(
                etype, value, tb, tb_offset=tb_offset):
            result = i.find("-> ")
            if result != -1:
                ende = i.find(" ", result + 3)
                if ende == -1:
                    x = "???"
                else:
                    x = str(i[result + 3:ende])

        short1 = ["Line " + str(x) + " --> "
                 ] + ipython.InteractiveTB.get_exception_only(etype, value)

        ausgabehtmlx = ""
        for xx in short1:
            ausgabehtmlx += str(reaesc.sub("", xx))

        switchCY = False
        if ausgabehtmlx.find("Error compiling Cython file") != -1:
            ausgabehtmlx = "Error compiling Cython file ..."
            switchCY = True

        short2 = ipython.InteractiveTB.structured_traceback(
            etype, value, tb, tb_offset=tb_offset)[2]

        if ausgabehtmlx.find("Error compiling Cython file") != -1:
            short2 = ipython.InteractiveTB.structured_traceback(
                etype, value, tb, tb_offset=tb_offset)[-1]

        ausgabehtmly = str(
            reaesc.sub(
                "",
                ipython.InteractiveTB.structured_traceback(etype,
                                                           value,
                                                           tb,
                                                           tb_offset=tb_offset)
                [2 if switchCY == False else -1].replace("\n", "<br>"),
            ))

        ausgabehtmly = "<br>" + ausgabehtmly[ausgabehtmly.find("<br>") + 4:]

        ausgabehtmly = ausgabehtmly.replace("<br>", "</b><br>")

        ausgabehtmly = ausgabehtmly.replace("<br>----> ", "<br>----> <b>")
        ausgabehtmly = ausgabehtmly.replace("<br>---> ", "<br>---> <b>")
        ausgabehtmly = ausgabehtmly.replace("<br>--> ", "<br>--> <b>")
        ausgabehtmly = ausgabehtmly.replace("<br>-> ", "<br>-> <b>")

    else:
        ausgabehtmlx = "Line xxxx"
        ausgabehtmly = "-.-"

        # syntax errors
        
        x = "???"
        short2 = ["Line " + str(x) + " --> Syntax Error"
                 ] + ipython.InteractiveTB.get_exception_only(etype, value)

        ausgabehtmly = str(
            reaesc.sub(
                "",
                ipython.InteractiveTB.get_exception_only(etype,
                                                         value)[0].replace(
                                                             "\n", "<br>"),
            ))

        textposi = ausgabehtmly.find("<br>") + 4
        textposi2 = ausgabehtmly.find("<br>", textposi) + 4
        endposi = ausgabehtmly.find("^<br>")
        errposi = endposi - textposi2

        errormsg = ausgabehtmly[endposi +
                                5:ausgabehtmly.find("<br>", endposi + 5)]
        ausgabehtmly = (
            "<br> ... " +
            ausgabehtmly[ausgabehtmly.find("<br>") + 4:textposi + errposi] +
            "<u>" +
            ausgabehtmly[ausgabehtmly.find("<br>") + 4 + errposi:textposi2] +
            "</u>") 
        
        x = "???"
        for nummer, i in enumerate(
                ipython.InteractiveTB.get_exception_only(etype, value)):

            result = i.find("line ")
            if result != -1:
                ende = i.find("\n", result + 5)
                if ende == -1:
                    x = "???"
                else:
                    x = str(i[result + 5:ende])
            else:
                pass

        short1 = [
            " Line " + str(x) + " Position " + str(endposi - textposi2 - 3) +
            " --> " + errormsg
        ]
        
        ausgabehtmlx = ""
        for xx in short1:
            ausgabehtmlx += str(reaesc.sub("", xx))

        # end syntaxerr

    if skip_traceback:
        display(
            HTML(ausgabehtml1 + ausgabehtmlx + ausgabehtml2 + ausgabehtmly +
                 ausgabehtml3))
        return ipython._showtraceback(
            etype,
            value,
            None,
        )
    else:
        return oldfunc(
            exc_tuple=None,
            filename=None,
            tb_offset=None,
            exception_only=False,
            running_compiled_code=False,
        )  


oldfunc = ipython.showtraceback

ipython.showtraceback = hide_traceback


def hide_syntaxerror(
    exc_tuple=None,
    filename=None,
    tb_offset=None,
    exception_only=False,
    running_compiled_code=False,
):

    if skip_traceback:
        return hide_traceback(filename=None, running_compiled_code=False)
    else:
        return oldsyntaxerr(filename=None, running_compiled_code=False)


oldsyntaxerr = ipython.showsyntaxerror
               
ipython.showsyntaxerror = hide_syntaxerror



def traceback(line):
    # print(line)
    # sio = StringIO(cell)

    global skip_traceback

    if line == "":
        skip_traceback = not (skip_traceback)

    if line == "on":
        skip_traceback = True

    if line == "off":
        skip_traceback = False

    if skip_traceback:
        print(
            "Skip-Traceback is now on - turn function off with %traceback off")
    else:
        print("Skip-Traceback is now off - turn funktion on with %traceback on")

    return


def load_ipython_extension(ipython):
    """This function is called when the extension is
    loaded. It accepts an IPython InteractiveShell
    instance. We can register the magic with the
    `register_magic_function` method of the shell
    instance."""
    ipython.register_magic_function(traceback, "line")


# https://stackoverflow.com/questions/46222753/how-do-i-suppress-tracebacks-in-jupyter
# https://stackoverflow.com/questions/25698448/how-to-embed-html-into-ipython-output
# https://www.w3schools.com/howto/howto_js_collapsible.asp
