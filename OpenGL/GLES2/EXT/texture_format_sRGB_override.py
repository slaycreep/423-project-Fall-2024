'''OpenGL extension EXT.texture_format_sRGB_override

This module customises the behaviour of the 
OpenGL.raw.GLES2.EXT.texture_format_sRGB_override to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides a new texture parameter to override the internal
	format of a texture object; allowing a non-sRGB format to be overridden to
	a corresponding sRGB format.  For example, an RGB8 texture can be overridden
	to SRGB8.  Such an override will cause the RGB components to be "decoded" from
	sRGB color space to linear as part of texture filtering.  This can be useful for
	applications where a texture was written with sRGB data using EXT_sRGB_write_control
	or when sampling from an EGLImage that is known to contain sRGB color values.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/texture_format_sRGB_override.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES2 import _types, _glgets
from OpenGL.raw.GLES2.EXT.texture_format_sRGB_override import *
from OpenGL.raw.GLES2.EXT.texture_format_sRGB_override import _EXTENSION_NAME

def glInitTextureFormatSrgbOverrideEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION