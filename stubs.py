#!/usr/bin/python3
"""
Expects to have `glew.h` and `gl-deprecated` on the same folder.
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


def main():
    defines = []
    inputs = []

    with open('gl-deprecated.h', 'r') as f:
        for line in f:
            if line.startswith("#define gl"):
                inputs.append(line[len("#define "):-1].split(' ')[0])
            elif line.startswith("#define GL_"):
                defines.append("#define {0} 0".format(line.split(' ')[2][:-1]))


    lookups = {}
    with open('glew.h', 'r') as f:
        for line in f:
            if line.startswith('GLAPI'):
                parts = line.split(' ')

                _type = parts[1]
                _GL_type = get_gl_type(_type)
                rest = get_rest(parts)
                name = parts[3]

                lookups[name] = "{_GL_type} DO_NOT_USE_{rest} {_GL_type}_RET".format(
                        _GL_type=_GL_type,
                        rest=rest,
                        )

    matches = []
    mismatches = []

    for i in inputs:
        match = lookups.get(i)
        if match is not None:
            matches.append(match)
        else:
            mismatches.append(i)

    with open('stubs.c', 'w') as f:
        f.write("""
/**
 * List automatically generated from `gl-deprecated.h` and `glew.h`
 */

/**
 * ENUM values
 */
""")
        f.write('\n'.join(defines))

        f.write("""

/**
 * Functions
 */
""")
        f.write('\n'.join(matches))

        f.write("""

/**
 * End of automatically generated list
 */
""")


    with open('stubs.err', 'w') as f:
        f.write('\n'.join(mismatches))

main()
