from libs.awdb.reader import *


try:
    from utils.awdb import extension
except ImportError:
    extension = None

from libs.awdb.const import (MODE_AUTO, MODE_MMAP, MODE_MMAP_EXT, MODE_FILE,
                             MODE_MEMORY, MODE_FD)
# from libs.awdb.decoder import InvalidDatabaseError


async def open_database(database, mode=MODE_AUTO):
    has_extension = extension and hasattr(extension,
                                                    'Reader')
    if (mode == MODE_AUTO and has_extension) or mode == MODE_MMAP_EXT:
        if not has_extension:
            raise ValueError(
                "MODE_MMAP_EXT requires the awdb.extension module to be available"
            )
        return extension.Reader(database)
    if mode in (MODE_AUTO, MODE_MMAP, MODE_FILE, MODE_MEMORY, MODE_FD):
        return reader.Reader(database, mode)
    raise ValueError('Unsupported open mode: {0}'.format(mode))


async def Reader(database):  
    return open_database(database)


__title__ = 'awdb'
__version__ = '1.5.2'
__author__ = ''
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2013-2020 AW, Inc.'
