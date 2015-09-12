#encoding=utf-8


def install_magics():
    import sys
    from os import path
    from IPython.lib.pretty import pretty as _pretty
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic
    from IPython.core.magic_arguments import (argument, magic_arguments,
                                              parse_argstring)
    from IPython.core.display import display_png, display_svg
    from IPython.core.getipython import get_ipython
    from scpy2.utils.program_finder import GraphvizPath

    sh = InteractiveShell.instance()

    def pretty(obj):
        import numpy as np
        if isinstance(obj, np.ndarray):
            return np.array2string(obj, separator=", ")
        else:
            return _pretty(obj)

    def show_arrays(arrays):
        from scpy2.utils.image import concat_images, display_image
        return display_image(concat_images(arrays))

    def get_section(filepath, section):
        import scpy2
        section_mark = "###{}###".format(section)
        lines = []
        flag = False
        if section == "0":
            flag = True
        for line in open(path.join(path.dirname(scpy2.__file__), filepath)):
            if not flag and line.startswith(section_mark):
                flag = True
                continue
            if flag:
                if line.startswith(section_mark):
                    break
                lines.append(line)
        return "".join(lines).rstrip()

    def run_dot(code, options=[], format='svg'):
        # mostly copied from sphinx.ext.graphviz.render_dot
        import os
        from subprocess import Popen, PIPE
        from sphinx.util.osutil import EPIPE, EINVAL

        if GraphvizPath is None:
            return "dot.exe not found"

        dot_args = [GraphvizPath] + options + ['-T', format]
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
    class ScPy2Magics(Magics):

        @line_magic
        def matplotlib_svg(self, line):
            ip = get_ipython()
            ip.run_cell("""
%config InlineBackend.figure_format = 'svg'
%config InlineBackend.rc = {'figure.figsize': (6.0, 3.0), 'figure.facecolor':(1.0, 1.0, 1.0)}
%matplotlib inline
            """)

        @line_magic
        def matplotlib_png(self, line):
            ip = get_ipython()
            ip.run_cell("""
%config InlineBackend.figure_format = 'png'
%config InlineBackend.rc = {'figure.figsize': (12.0, 6.0), 'figure.facecolor':(1.0, 1.0, 1.0)}
%matplotlib inline
            """)

        @cell_magic
        def next_input(self, line, cell):
            ip = get_ipython()
            ip.run_cell(cell, silent=True)
            result = ip.user_ns[line]
            ip.set_next_input(result)

        @cell_magic
        def disabled(self, line, cell):
            pass

        @cell_magic
        def language(self, line, cell):
            pass

        @line_magic
        def col(self, line):
            """
            %col number_of_column code
            """
            pos = line.find(" ")
            n = int(line[:pos])
            code = line[pos+1:]
            result = pretty(sh.ev(code)).split("\n")
            max_width = max(len(line) for line in result) + 3
            result = [line.ljust(max_width) for line in result]
            result = "\n".join(["".join(result[i:i+n]) for i in xrange(0, len(result), n)])
            print result

        @line_magic
        def omit(self, line):
            """
            %omit number_of_line code
            """
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
            old_stdout = sys.stdout

            try:
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
            if result:
                print "\n".join(sh.display_formatter.formatters["text/plain"](result).split("\n")[:count])
                print "..."

        @line_magic("C")
        def _C(self, line):
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

        @line_magic
        def exec_python(self, line):
            """
            pass all the arguments to a new python process
            """
            import subprocess
            cmd = "python " + line
            subprocess.Popen(cmd, shell=True)

        @magic_arguments()
        @argument('language', help='the language of the file')
        @argument('path', help='the file path in scpy2 folder')
        @argument('section', help='the include section')
        @argument("-r", "--run", action='store_true', help='run the included code')
        @cell_magic
        def include(self, line, cell):
            """
            include section of the files in scpy2 folder
            """
            import json
            ip = get_ipython()
            args = parse_argstring(self.include, line)
            language = args.language
            filepath = args.path
            section = args.section
            run = args.run
            first_line = "%%include " + line
            section_text = get_section(filepath, section)
            if run:
                ip.run_cell(section_text)
            text = json.dumps(unicode(first_line) + u"\n" + section_text.decode("utf8"))
            code = """%%javascript
(function(pattern, text){{
    var cells = IPython.notebook.get_cells();
    for (var i = 0; i < cells.length; i++) {{
        var cell = cells[i];
        if (cell.get_text().indexOf(pattern) == 0){{
            cell.set_text(text);
        }}
    }}
}})({0}, {1});
    """.format(json.dumps(first_line), text)
            ip.run_cell(code)            
            from IPython import display
            display.clear_output()

        @cell_magic
        def nopage(self, line, cell):
            def print_page(s):
                print s
            from IPython.core import page
            old_page = page.page
            page.page = print_page
            ip = get_ipython()
            ip.run_cell(cell)
            page.page = old_page

        @line_magic
        def array_image(self, line):
            import numpy as np

            arrays = []
            for item in [sh.ev(code) for code in line.split(";")]:
                if isinstance(item, np.ndarray):
                    arrays.append(item)
                else:
                    arrays.extend(item)

            return show_arrays(arrays)

        @cell_magic
        def func_debug(self, line, cell):
            import inspect
            ip = get_ipython()
            func = ip.ev(line)
            filename = inspect.getabsfile(func)
            bp_line = inspect.getsourcelines(func)[1]
            instance = ip.magics_manager.registry["ExecutionMagics"]
            instance._run_with_debugger(cell, instance.shell.user_ns, filename, bp_line)

        @line_magic
        def init_sympy_printing(self, line):
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

        @line_magic
        def sympy_latex(self, line):
            from sympy import latex
            from IPython.display import Latex, display
            ip = get_ipython()
            latex = Latex("$${}$$".format(latex(ip.ev(line))))
            display(latex)

        @cell_magic
        def mlab_plot(self, line, cell):
            from mayavi import mlab
            ip = get_ipython()
            offscreen = mlab.options.offscreen
            try:
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
            finally:
                mlab.options.offscreen = offscreen

        @cell_magic
        def thread(self, line, cell):
            import threading
            ip = get_ipython()
            env = ip.user_global_ns

            def f():
                exec cell in env

            thread = threading.Thread(target=f, name="__magic_thread__" + line)
            thread.start()

        @line_magic
        def find(self, line):
            from IPython.core.getipython import get_ipython
            from fnmatch import fnmatch

            items = line.split()
            patterns, target = items[:-1], items[-1]
            ipython = get_ipython()
            names = dir(ipython.ev(target))

            results = []
            for pattern in patterns:
                for name in names:
                    if fnmatch(name, pattern):
                        results.append(name)
            return results

        @magic_arguments()
        @argument('-l', '--lines', help='max lines', type=int, default=100)
        @argument('-c', '--chars', help='max chars', type=int, default=10000)
        @cell_magic
        def cut(self, line, cell):
            from IPython.core.getipython import get_ipython
            from sys import stdout
            args = parse_argstring(self.cut, line)
            max_lines = args.lines
            max_chars = args.chars

            counters = dict(chars=0, lines=0)

            def write(string):
                counters["lines"] += string.count("\n")
                counters["chars"] += len(string)

                if counters["lines"] >= max_lines:
                    raise IOError("Too many lines")
                elif counters["chars"] >= max_chars:
                    raise IOError("Too many characters")
                else:
                    old_write(string)

            try:
                old_write, stdout.write = stdout.write, write
                ipython = get_ipython()
                ipython.run_cell(cell)
            finally:
                del stdout.write

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

    get_ipython().register_magics(ScPy2Magics)
    get_ipython().register_magics(GraphvizMagic)



