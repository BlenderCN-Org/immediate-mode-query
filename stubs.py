#!/usr/bin/python3
"""
Expects blender base folder as argument.

Outputs: `stubs.out` for the matches and `stubs.err` for ths mismatches

Example:
========
Input: gl-deprecated.h
Lookup Table: glew.h
Output: output.c

Input A:
#define glAccum DO_NOT_USE_glAccum

Lookup Table:
GLAPI void GLAPIENTRY glAccum (GLenum op, GLfloat value);

Output:
_GL_VOID DO_NOT_USE_glAccum (GLenum op, GLfloat value) _GL_VOID_RET


Input B:
#define glRenderMode DO_NOT_USE_glRenderMode

Lookup Table:
GLAPI GLint GLAPIENTRY glRenderMode (GLenum mode);

Output:
_GL_INT DO_NOT_USE_glRenderMode (GLenum mode) _GL_INT_RET


Input C:
#define GL_SOURCE2_RGB DO_NOT_USE_GL_SOURCE2_RGB

Output:
#define DO_NOT_USE_GL_SOURCE2_RGB 0
"""

import fnmatch
import os
import re
import sys


PREAMBLE = """
/**
 * List automatically generated from `gl-deprecated.h` and `glew.h`
 */
 """

ENUMS = """

/**
 * ENUM values
 */
"""

FUNCTIONS = """

/**
 * Functions
 */
"""

END = """

/**
 * End of automatically generated list
 */
"""


def get_gl_type(_type):
    lookup = {
        'GLboolean': '_GL_BOOL',
        'GLenum': '_GL_ENUM',
        'GLint': '_GL_INT',
        'GLuint': '_GL_UINT',
        'void': '_GL_VOID',
        'const': 'NOT_IMPLEMENTED',
        }

    gl_type = lookup.get(_type)
    assert gl_type is not None, _type
    return gl_type


def get_rest(parts):
    _all = ' '.join(parts[3:])
    return _all[:-2]


def get_filepaths(argv):
    if len(argv) != 1:
        print("Invalid number of arguments, "
              "expect `stubs.py /full/path/to/blender/source`")
        print("Got: {0}".format(argv))
        sys.exit(-1)

    base_blender = argv[0]

    if not os.path.isdir(base_blender):
        print("Path is not a directory: \"{0}\"".format(base_blender))
        sys.exit(-2)

    gl_deprecated = os.path.join(
        base_blender,
        'intern',
        'glew-mx',
        'intern',
        'gl-deprecated.h',
        )

    if not os.path.exists(gl_deprecated):
        print("Could not find: \"{0}\"".format(gl_deprecated))
        sys.exit(-3)

    glew = os.path.join(
        base_blender,
        'extern',
        'glew',
        'include',
        'GL',
        'glew.h',
        )

    if not os.path.exists(glew):
        print("Could not find: \"{0}\"".format(glew))
        sys.exit(-4)

    filepaths = {
        'base_blender': base_blender,
        'gl_deprecated': gl_deprecated,
        'glew': glew,
        }

    return filepaths


def all_files_get(base_folder):
    all_files = []

    includes = ('*.c', '*.cpp', '*.h', '*.m', '*.mm')
    excludes = (
        '*.git', '*.svn',
        'bgl.c',
        'GPU_legacy_subs.h',
        'blenderplayer',
        'extern',
        'gameengine',
        'tests',
        'tools',
        )

    base_folder = os.path.join(base_folder, 'source', 'blender')

    for root, dirs, files in os.walk(base_folder, topdown=True):
        # excludes can be done with fnmatch.filter and complementary set,
        # but it's more annoying to read.
        dirs[:] = [d for d in dirs if d not in excludes]
        for pat in includes:
            for f in fnmatch.filter(files, pat):
                all_files.append(os.path.join(root, f))

    return all_files


def found_in_blender(all_files, word):
    for f in all_files:
        for line in open(f, 'r'):
            if word in line:
                return True
    return False


def main(argv):
    filepaths = get_filepaths(argv)

    enums = []
    functions = []

    with open(filepaths['gl_deprecated']) as f:
        for line in f:
            parts = line[:-1].split(' ')

            if parts[0] != '#define':
                continue

            if parts[1].startswith('gl'):
                functions.append(parts[1])

            elif parts[1].startswith('GL_'):
                enums.append((parts[1], parts[2]))

    lookups = {}
    with open(filepaths['glew'], 'r') as f:
        for line in f:
            if line.startswith('GLAPI'):
                parts = line.split(' ')

                _type = parts[1]
                _GL_type = get_gl_type(_type)
                rest = get_rest(parts)
                name = parts[3]

                lookups[name] = '{_GL_type} DO_NOT_USE_{rest} {_GL_type}_RET'.format(
                    _GL_type=_GL_type,
                    rest=rest,
                    )

    # We now check if those functions are even called in Blender
    # Otherwise we shouldn't bother
    all_files = all_files_get(filepaths['base_blender'])
    print("Grepping the enums")
    blender_enums = {e[1] for e in enums if found_in_blender(all_files, e[0])}
    print("Grepping the functions")
    blender_functions = {w for w in functions if found_in_blender(all_files, w)}

    blender_funcs_okay = []
    blender_funcs_error = []

    for f in blender_functions:
        match = lookups.get(f)
        if match is not None:
            blender_funcs_okay.append(match)
        else:
            blender_funcs_error.append(f)

    print('Writing output')
    with open('stubs.c', 'w') as f:
        f.write(PREAMBLE)

        if blender_enums:
            f.write(ENUMS)
            formatted_enums = ('#define {0} 0'.format(e) for e in blender_enums)
            f.write('\n'.join(formatted_enums))

        if blender_funcs_okay:
            f.write(FUNCTIONS)
            f.write('\n'.join(blender_funcs_okay))

        f.write(END)

    with open('stubs.err', 'w') as f:
        f.write('\n'.join(blender_funcs_error))

    if blender_funcs_error:
        print("Results written to stubs.err and stubs.c")
    else:
        print("Results written to stubs.c")


if __name__ == "__main__":
    main(sys.argv[1:])
