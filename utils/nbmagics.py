def install_magics():
    import sys
    from os import path
    from ConfigParser import ConfigParser
    from IPython.core.magic import register_line_magic, register_cell_magic
    from IPython.lib.pretty import pretty as _pretty
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic
    from IPython.core.magic_arguments import (argument, magic_arguments,
                                              parse_argstring)
    from IPython.core.display import display_png, display_svg
    from IPython.core.getipython import get_ipython
    from collections import OrderedDict

    sh = InteractiveShell.instance()

    def pretty(obj):
        import numpy as np
        if isinstance(obj, np.ndarray):
            return np.array2string(obj, separator=", ")
        else:
            return _pretty(obj)

    def show_arrays(arrays):
        import io
        from matplotlib.image import imsave
        from IPython import display
        import numpy as np
        margin = 10
        width = sum(arr.shape[1] for arr in arrays) + (len(arrays)-1)*margin
        height = max(arr.shape[0] for arr in arrays)
        img = np.empty((height, width, 3), dtype=np.uint8)
        img.fill(255)
        x = 0
        for arr in arrays:
            if arr.dtype in (np.float32, np.float64):
                arr = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
            h, w = arr.shape[:2]
            if arr.ndim == 2:
                arr = arr[:, :, None]
            elif arr.ndim == 3:
                arr = arr[:, :, :3]
            img[:h, x:x+w, :] = arr[:, :, :]
            x += w + margin

        buf = io.BytesIO()
        imsave(buf, img)
        return display.Image(buf.getvalue())

    @register_line_magic
    def exec_python(line):
        import subprocess
        cmd = "python " + line
        subprocess.Popen(cmd, shell=True)

    @register_line_magic
    def col(line):
        pos = line.find(" ")
        n = int(line[:pos])
        code = line[pos+1:]
        result = pretty(sh.ev(code)).split("\n")
        max_width = max(len(line) for line in result) + 3
        result = [line.ljust(max_width) for line in result]
        result = "\n".join(["".join(result[i:i+n])
            for i in xrange(0, len(result), n)])
        print result

    @register_line_magic
    def omit(line):
        import sys
        pos = line.find(" ")
        try:
            count = int(line[:pos])
            line = line[pos+1:]
        except ValueError:
            count = 4

        lines = []
        def write(s):
            lines.append(s)

        def flush():
            pass

        write.flush = flush

        write.write = write
        try:
            old_stdout = sys.stdout
            sys.stdout = write
            result = sh.ev(line)
        finally:
            sys.stdout = old_stdout

        if lines:
            stdout = "".join(lines).split("\n")[:count]
            indent = len(stdout[-1]) - len(stdout[-1].lstrip())
            stdout.append(" "*indent + "...")
            stdout_lines = "\n".join(stdout)
            sys.stdout.write(stdout_lines)
        #try:
        #    return result[:count]
        #except:
        if result:
            print "\n".join(sh.display_formatter.formatters["text/plain"](result).split("\n")[:count])
            print "..."

    @register_line_magic("C")
    def _C(line):
        global results
        from itertools import izip_longest
        pos = line.find(" ")
        try:
            gap = int(line[:pos])
            line = line[pos+1:]
        except ValueError:
            gap = 2

        for idx, sec in enumerate(line.split(";;")):
            if idx > 0:
                print
            codes = [x.strip() for x in sec.split(";")]
            results = [[code] for code in codes]
            for i, code in enumerate(codes):
                results[i].extend(pretty(sh.ev(code)).split("\n"))

            results = [list(row) for row in zip(*list(izip_longest(*results, fillvalue="")))]

            for i, col in enumerate(results):
                width = max(len(row) for row in col)
                col.insert(1, "-"*width)
                col[0] = col[0].center(width)
                col[2:] = [row.ljust(width) for row in col[2:]]

            for row in zip(*results):
                print (" "*gap).join(row)

    @register_cell_magic
    def cython_ann(line, cell):
        from Cython.Compiler.Main import compile as cy_compile
        from Cython.Compiler.CmdLine import parse_command_line
        from IPython.core import display
        import re

        with open("demo.pyx","wb") as f:
            f.write(cell.strip().encode("utf8"))
        options, sources = parse_command_line(["-a", "demo.pyx"])
        cy_compile(sources, options)
        with open("demo.html") as f:
            html = f.read().decode("utf8")

        html = u"\n".join([line for line in html.split("\n") if not line.startswith("<p>")])
        html = html.replace(u"display: none;", u"")
        html= re.sub(u"/\*.+?\*/.", u"", html, flags=re.DOTALL | re.MULTILINE)
        javascript = u"""
        <script>
        $("pre.code").css("background-color", "#ffffff").hide()
            .css("border-left", "2px solid #cccccc")
            .css("margin-left", "10px");
        $("pre.line").attr("onclick", "").click(function(){$(this).next().slideToggle();return 0;})
            .css("border-bottom", "1px solid #cccccc");
        $("span.error_goto").hide();
        </script>
        """
        display.display(display.HTML(html))
        display.display(display.HTML(javascript))

    parts = {}

    @register_cell_magic
    def disabled(line, cell):
        pass

    @register_cell_magic
    def language(line, cell):
        pass

    @register_cell_magic
    def cython_part(line, cell):
        parts[line] = cell

    @register_line_magic
    def run_cython_parts(line):
        keys = line.split()
        code = "\n".join([parts[key] for key in keys])
        ip = get_ipython()
        ip.run_cell(code)

    @register_line_magic
    def merge_cython_parts(line):
        keys = line.split()
        code = "\n\n".join([parts[key] for key in keys])
        ip = get_ipython()
        ip.set_next_input(code)

    @register_cell_magic
    def next_input(line, cell):
        ip = get_ipython()
        ip.run_cell(cell, silent=True)
        result = ip.user_ns[line]
        ip.set_next_input(result)

    @register_line_magic
    def matplotlib_svg(line):
        ip = get_ipython()
        ip.run_cell("""
%config InlineBackend.figure_format = 'svg'
%config InlineBackend.rc = {'figure.figsize': (6.0, 3.0), 'figure.facecolor':(1.0, 1.0, 1.0)}
%matplotlib inline
        """)

    @register_line_magic
    def matplotlib_png(line):
        ip = get_ipython()
        ip.run_cell("""
%config InlineBackend.figure_format = 'png'
%config InlineBackend.rc = {'figure.figsize': (12.0, 6.0), 'figure.facecolor':(1.0, 1.0, 1.0)}
%matplotlib inline
        """)


    @magics_class
    class ScPy2Magics(Magics):
        @line_magic
        def ets(self, parameter_s=''):
            """Choose backend for ETS GUI

            %ets wx|qt
            """
            opts, arg = self.parse_options(parameter_s, '')
            if arg == "qt":
                import sip, os
                sip.setapi('QString', 2)
                sip.setapi('QVariant', 2)
                os.environ['ETS_TOOLKIT'] = 'qt4'
            elif arg == "wx":
                import os
                os.environ['ETS_TOOLKIT'] = 'wx'
            else:
                from IPython.utils.warn import error
                error("argument of ets must be wx or qt")
            self.shell.enable_gui(arg)

    get_ipython().register_magics(ScPy2Magics)

    @register_cell_magic
    def nopage(line, cell):
        def print_page(s):
            print s
        from IPython.core import page
        old_page = page.page
        page.page = print_page
        ip = get_ipython()
        ip.run_cell(cell)
        page.page = old_page

    @register_line_magic
    def cv_image(line):
        import numpy as np
        import io
        import cv2
        from IPython import display

        arrays = [sh.ev(code) for code in line.split(";")]
        margin = 10
        width = sum(arr.shape[1] for arr in arrays) + (len(arrays)-1)*margin
        height = max(arr.shape[0] for arr in arrays)
        img = np.empty((height, width, 3), dtype=np.uint8)
        img.fill(255)
        x = 0
        for arr in arrays:
            h, w = arr.shape[:2]
            if arr.ndim == 2:
                arr = arr[:, :, None]
            elif arr.ndim == 3:
                arr = arr[:, :, :3]
            img[:h, x:x+w, :] = arr[:, :, :]
            x += w + margin

        ret, buf = cv2.imencode(".png", img)
        return display.Image(buf.tostring())

    @register_line_magic
    def array_image(line):
        import numpy as np
        import io
        from matplotlib.image import imsave
        from IPython import display

        arrays = []
        for item in [sh.ev(code) for code in line.split(";")]:
            if isinstance(item, np.ndarray):
                arrays.append(item)
            else:
                arrays.extend(item)

        return show_arrays(arrays)

    def setup_digital_axes(fig):
        fig.subplots_adjust(hspace=0)
        for ax in fig.axes:
            ax.yaxis.set_ticks([])
        first_ax, last_ax = fig.axes[0], fig.axes[-1]
        first_ax.xaxis.set_ticks_position("top")
        first_ax.xaxis.set_ticklabels([])
        last_ax.xaxis.set_ticks_position("bottom")
        for ax in fig.axes:
            if ax is not first_ax:
                ax.spines["top"].set_visible(False)
            if ax is not last_ax:
                ax.spines["bottom"].set_visible(False)
            if ax not in (first_ax, last_ax):
                ax.xaxis.set_ticks([])
            ax.yaxis.set_ticks([])
            ax.set_ylim(-0.5, 1.5)
        fig.canvas.draw()

    DOT_PATH = r"C:\Program Files (x86)\Graphviz2.36\bin\dot.exe"

    def run_dot(code, options=[], format='svg'):
        # mostly copied from sphinx.ext.graphviz.render_dot
        import os
        from subprocess import Popen, PIPE
        from sphinx.util.osutil import EPIPE, EINVAL

        dot_args = [DOT_PATH] + options + ['-T', format]
        if os.name == 'nt':
            # Avoid opening shell window.
            # * https://github.com/tkf/ipython-hierarchymagic/issues/1
            # * http://stackoverflow.com/a/2935727/727827
            p = Popen(dot_args, stdout=PIPE, stdin=PIPE, stderr=PIPE,
                      creationflags=0x08000000)
        else:
            p = Popen(dot_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        wentwrong = False
        try:
            # Graphviz may close standard input when an error occurs,
            # resulting in a broken pipe on communicate()
            stdout, stderr = p.communicate(code.encode('utf-8'))
        except (OSError, IOError) as err:
            if err.errno != EPIPE:
                raise
            wentwrong = True
        except IOError as err:
            if err.errno != EINVAL:
                raise
            wentwrong = True
        if wentwrong:
            # in this case, read the standard output and standard error streams
            # directly, to get the error message(s)
            stdout, stderr = p.stdout.read(), p.stderr.read()
            p.wait()
        if p.returncode != 0:
            raise RuntimeError('dot exited with error:\n[stderr]\n{0}'
                               .format(stderr.decode('utf-8')))
        return stdout


    @magics_class
    class GraphvizMagic(Magics):

        @magic_arguments()
        @argument(
            '-f', '--format', default='svg', choices=('png', 'svg'),
            help='output format (png/svg)'
        )
        @argument(
            'code', default=[], nargs=1,
            help='python code that return dot code'
        )
        @line_cell_magic
        def dot(self, line="", cell=None):
            """Draw a figure using Graphviz dot command."""
            args = parse_argstring(self.dot, line)

            if cell is None:
                sh = get_ipython()
                cell = sh.ev(args.code[0])

            image = run_dot(cell, [], format=args.format)

            if args.format == 'png':
                display_png(image, raw=True)
            elif args.format == 'svg':
                display_svg(image, raw=True)

    get_ipython().register_magics(GraphvizMagic)

    from collections import defaultdict
    from IPython.core.magic import Magics, magics_class, cell_magic
    from IPython.core import magic_arguments

    @magics_class
    class CythonPartsMagic(Magics):

        def __init__(self, shell):
            super(CythonPartsMagic, self).__init__(shell)
            self.parts = defaultdict(dict)

        @cell_magic
        def cythonpart(self, line, cell):
            name, index = line.split()
            index = int(index)
            parts = self.parts[name]
            parts[index] = cell
            cells = [v for k,v in sorted(parts.items())]
            cell = "\n".join(cells)
            cython = self.shell.find_cell_magic("cython")
            cython("", cell)

    @register_cell_magic
    def pep8(line, cell):
        import autopep8

        class fix_repr(object):

            def __init__(self, obj):
                self.obj = obj

            def __repr__(self):
                return self.obj.encode("utf8")

        if cell.startswith("%%"):
            lines = cell.split("\n")
            first_line = lines[0]
            cell = "\n".join(lines[1:])
        else:
            first_line = ""

        cell = autopep8.fix_code(cell)
        if first_line:
            cell = first_line + "\n" + cell
        cell = cell.replace("\n\n\n", "\n\n")
        return fix_repr(cell)

    def read_config(fn):
        config = OrderedDict()
        if not path.exists(fn):
            return config
        parser = ConfigParser()
        parser.read(fn)
        for section in parser.sections():
            options_dict = OrderedDict()
            config[section] = options_dict
            options = parser.options(section)
            for option in options:
                options_dict[option] = parser.get(section, option)
        return config

    def write_config(fn, config):
        with open(fn, "w") as f:
            for section, options_dict in config.items():
                f.write("[{}]\n".format(section))
                for option, value in options_dict.items():
                    f.write("{}={}\n".format(option, value))
                f.write("\n")

    @register_line_magic
    def compiler(line):
        from os import path
        compiler = line.strip()
        sys_dir = path.dirname(sys.modules['distutils'].__file__)
        sys_file = path.join(sys_dir, "distutils.cfg")
        config = read_config(sys_file)
        if "build" not in config:
            config["build"] = OrderedDict()
        build_options = config["build"]
        build_options["compiler"] = compiler
        write_config(sys_file, config)

    def get_section(filepath, section):
        from os import path
        import scpy2
        section = "###{}###".format(section)
        lines = []
        flag = False
        for line in file(path.join(path.dirname(scpy2.__file__), filepath)):
            if not flag and line.startswith(section):
                flag = True
                continue
            if flag:
                if line.startswith(section):
                    break
                lines.append(line)
        return "".join(lines).rstrip()

    @register_cell_magic
    def include(line, cell):
        import json
        language, filepath, section = line.split()
        section = int(section)
        first_line = "%%include " + line
        section_text = get_section(filepath, section)
        text = json.dumps(unicode(first_line) + u"\n" + section_text.decode("utf8"))
        code = """%%javascript
        replace_cell({0}, {1});
""".format(json.dumps(first_line), text)
        ip.run_cell(code)

    @register_cell_magic
    def func_debug(line, cell):
        import inspect
        ip = get_ipython()
        func = ip.ev(line)
        filename = inspect.getabsfile(func)
        bp_line = inspect.getsourcelines(func)[1]
        instance = ip.magics_manager.registry["ExecutionMagics"]
        instance._run_with_debugger(cell, instance.shell.user_ns, filename, bp_line)

    @register_line_magic
    def init_sympy_printing(line):
        from sympy import init_printing
        init_printing()
        ip = get_ipython()
        latex = ip.display_formatter.formatters["text/latex"]
        for key in latex.type_printers.keys():
            if key.__module__ == "__builtin__":
                del latex.type_printers[key]
        png = ip.display_formatter.formatters["image/png"]
        for key in png.type_printers.keys():
            if key.__module__ == "__builtin__":
                del png.type_printers[key]

    @register_line_magic
    def sympy_latex(line):
        from sympy import latex
        from IPython.display import Latex
        ip = get_ipython()
        return Latex(latex(ip.ev(line)))

    @register_cell_magic
    def mlab_plot(line, cell):
        from mayavi import mlab
        ip = get_ipython()
        mlab.options.offscreen = True
        if line:
            width, height = [int(x) for x in line.split()]
        else:
            width, height = 800, 600
        scene = mlab.figure(size=(width, height))
        scene.scene.background = 1, 1, 1
        ip.run_cell(cell)
        from scpy2 import vtk_scene_to_array
        img = vtk_scene_to_array(scene.scene)
        return show_arrays([img])

    ip = get_ipython()
    ip.register_magics(CythonPartsMagic)