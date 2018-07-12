# -*- coding: utf-8 -*-
import os
import tempfile
import shutil
import glob

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

_fixturedir = os.path.join(os.path.dirname(__file__), 'fixture')
_fakecmd = os.path.join(os.path.dirname(__file__), 'fakecmd.py')


def readfile(_outdir, fname):
    with open(os.path.join(_outdir, fname), 'r') as f:
        return f.read()


def runsphinx(_outdir, _srcdir, text, builder, confoverrides):
    f = open(os.path.join(_srcdir, 'index.rst'), 'w')
    try:
        f.write(text)
    finally:
        f.close()
    with docutils_namespace():
        app = Sphinx(_srcdir, _fixturedir, _outdir, _outdir, builder,
                     confoverrides)
        app.build()


def with_runsphinx(builder, confoverrides=None):
    if confoverrides is None:
        confoverrides = {
            'plantuml': _fakecmd,
            'graphviz': _fakecmd,
        }

    def wrapfunc(func):
        _tempdir = tempfile.mkdtemp()
        _srcdir = os.path.join(_tempdir, 'src')
        _outdir = os.path.join(_tempdir, 'out')
        os.mkdir(_srcdir)

        def test():
            src = '\n'.join(l[4:] for l in func.__doc__.splitlines()[2:])
            os.mkdir(_outdir)
            try:
                runsphinx(_outdir, _srcdir, src, builder, confoverrides)
                func(_outdir)
            finally:
                os.unlink(os.path.join(_srcdir, 'index.rst'))
                shutil.rmtree(_outdir)

        test.__name__ = func.__name__
        return test

    return wrapfunc


@with_runsphinx('html')
def test_buildhtml_simple(_outdir):
    """Generate simple HTML

    .. sadisplay::
        :module: model
    """
    files = glob.glob(os.path.join(_outdir, '_images', 'sadisplay-*.png'))
    assert len(files) == 1
    assert '<img src="_images/sadisplay' in readfile(_outdir, 'index.html')

    content = readfile(_outdir, files[0])
    assert 'Admin' in content
    assert 'User' in content
    assert 'Address' in content


@with_runsphinx('html')
def test_buildhtml_as_link(_outdir):
    """Generate simple HTML with link

    .. sadisplay::
        :module: model
        :link:
    """
    files = glob.glob(os.path.join(_outdir, '_images', 'sadisplay-*.png'))
    assert len(files) == 1
    assert '<a href="_images/sadisplay' in readfile(_outdir, 'index.html')


@with_runsphinx('latex')
def test_buildlatex_simple(_outdir):
    """Generate simple LaTeX

    .. sadisplay::
       :module: model
       :exclude: Admin
    """
    files = glob.glob(os.path.join(_outdir, 'sadisplay-*.png'))
    assert len(files) == 1
    assert '\includegraphics{sadisplay-' in readfile(_outdir,
                                                     'sadisplay_fixture.tex')

    content = readfile(_outdir, files[0])
    assert 'Admin' not in content
    assert 'User' in content
    assert 'Address' in content
