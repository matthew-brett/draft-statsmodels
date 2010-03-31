"""
Input/Output tools for working with binary data.

The Stata input tools were originally written by Joe Presbrey as part of PyDTA.

You can find more information here http://presbrey.mit.edu/PyDTA

See also
---------
numpy.lib.io
"""

from struct import unpack, calcsize
import sys
import numpy as np
from numpy.lib._iotools import _is_string_like


### Helper classes for StataReader ###

class _StataMissingValue(object):
    """
    An observation's missing value.

    Parameters
    -----------
    offset
    value

    Attributes
    ----------
    string
    value

    Notes
    -----
    More information: <http://www.stata.com/help.cgi?missing>
    """

    def __init__(self, offset, value):
        self._value = value
        if type(value) is int or type(value) is long:
            self._str = value-offset is 1 and \
                    '.' or ('.' + chr(value-offset+96))
        else:
            self._str = '.'
    string = property(lambda self: self._str, doc="The Stata representation of \
the missing value: '.', '.a'..'.z'")
    value = property(lambda self: self._value, doc='The binary representation \
of the missing value.')
    def __str__(self): return self._str
    __str__.__doc__ = string.__doc__

class _StataVariable(object):
    """
    A dataset variable.  Not intended for public use.

    Parameters
    ----------
    variable_data

    Attributes
    -----------
    format : str
        Stata variable format.  See notes for more information.
    index : int
        Zero-index column index of variable.
    label : str
        Data Label
    name : str
        Variable name
    type : str
        Stata data type.  See notes for more information.
    value_format : str
        Value format.

    Notes
    -----
    More information: http://www.stata.com/help.cgi?format
    """
    def __init__(self, variable_data):
        self._data = variable_data

    def __int__(self):
        return self.index

    def __str__(self):
        return self.name
    index = property(lambda self: self._data[0], doc='the variable\'s index \
within an observation')
    type = property(lambda self: self._data[1], doc='the data type of \
variable\n\nPossible types are:\n{1..244:string, b:byte, h:int, l:long, \
f:float, d:double)')
    name = property(lambda self: self._data[2], doc='the name of the variable')
    format = property(lambda self: self._data[4], doc='the variable\'s Stata \
format')
    value_format = property(lambda self: self._data[5], doc='the variable\'s \
value format')
    label = property(lambda self: self._data[6], doc='the variable\'s label')
    __int__.__doc__ = index.__doc__
    __str__.__doc__ = name.__doc__

class StataReader(object):
    """
    Stata .dta file reader.

    Provides methods to return the metadata of a Stata .dta file and
    a generator for the data itself.

    Parameters
    ----------
    file : file-like
        A file-like object representing a Stata .dta file.

    missing_values : bool
        If missing_values is True, parse missing_values and return a
        Missing Values object instead of None.

    See also
    --------
    scikits.statsmodels.lib.io.genfromdta

    Notes
    -----
    This is known only to work on file formats 113 (Stata 8/9) and 114
    (Stata 10/11).  Needs to be tested on older versions.
    Known not to work on format 104, 108.

    For more information about the .dta format see
    http://www.stata.com/help.cgi?dta
    http://www.stata.com/help.cgi?dta_113
    """

    _header = {}
    _data_location = 0
    _col_sizes = ()
    _has_string_data = False
    _missing_values = False
    TYPE_MAP = range(251)+list('bhlfd')
    MISSING_VALUES = { 'b': (-127,100), 'h': (-32767, 32740), 'l':
            (-2147483647, 2147483620), 'f': (-1.701e+38, +1.701e+38), 'd':
            (-1.798e+308, +8.988e+307) }

    def __init__(self, fname, missing_values=False):
        self._missing_values = missing_values
        self._parse_header(fname)

    def file_headers(self):
        """
        Returns all .dta file headers.

        out: dict
            Has keys typlist, data_label, lbllist, varlist, nvar, filetype,
            ds_format, nobs, fmtlist, vlblist, time_stamp, srtlist, byteorder
        """
        return self._header

    def file_format(self):
        """
        Returns the file format.

        Returns
        -------
        out : int

        Notes
        -----
        Format 113: Stata 8/9
        Format 114: Stata 10/11
        """
        return self._header['ds_format']

    def file_label(self):
        """
        Returns the dataset's label.

        Returns
        ------
        out: string
        """
        return self._header['data_label']

    def file_timestamp(self):
        """
        Returns the date and time Stata recorded on last file save.

        Returns
        -------
        out : str
        """
        return self._header['time_stamp']

    def variables(self):
        """
        Returns a list of the dataset's StataVariables objects.
        """
        return map(_StataVariable, zip(range(self._header['nvar']),
            self._header['typlist'], self._header['varlist'],
            self._header['srtlist'],
            self._header['fmtlist'], self._header['lbllist'],
            self._header['vlblist']))

    def dataset(self, as_dict=False):
        """
        Returns a Python generator object for iterating over the dataset.


        Parameters
        ----------
        as_dict : bool, optional
            If as_dict is True, yield each row of observations as a dict.
            If False, yields each row of observations as a list.

        Returns
        -------
        Generator object for iterating over the dataset.  Yields each row of
        observations as a list by default.

        Notes
        -----
        If missing_values is True during instantiation of StataReader then
        observations with _StataMissingValue(s) are not filtered and should
        be handled by your applcation.
        """

        try:
            self._file.seek(self._data_location)
        except Exception:
            pass

        if as_dict:
            vars = map(str, self.variables())
            for i in range(len(self)):
                yield dict(zip(vars, self._next()))
        else:
            for i in range(self._header['nobs']):
                yield self._next()

    ### Python special methods

    def __len__(self):
        """
        Return the number of observations in the dataset.

        This value is taken directly from the header and includes observations
        with missing values.
        """
        return self._header['nobs']

    def __getitem__(self, k):
        """
        Seek to an observation indexed k in the file and return it, ordered
        by Stata's output to the .dta file.

        k is zero-indexed.  Prefer using R.data() for performance.
        """
        if not (type(k) is int or type(k) is long) or k < 0 or k > len(self)-1:
            raise IndexError(k)
        loc = self._data_location + sum(self._col_size()) * k
        if self._file.tell() != loc:
            self._file.seek(loc)
        return self._next()

    ### Private methods

    def _null_terminate(self, s):
        try:
            return s.lstrip('\x00')[:s.index('\x00')]
        except Exception:
            return s

    def _parse_header(self, file_object):
        self._file = file_object

        # parse headers
        self._header['ds_format'] = unpack('b', self._file.read(1))[0]

        if self._header['ds_format'] not in [113,114]:
            raise ValueError, "Only file formats 113 and 114 (Stata 9, 10, 11)\
 are supported.  Got format %s.  Please report if you think this error is \
incorrect." % self._header['ds_format']
        byteorder = self._header['byteorder'] = unpack('b',
                self._file.read(1))[0]==0x1 and '>' or '<'
        self._header['filetype'] = unpack('b', self._file.read(1))[0]
        self._file.read(1)
        nvar = self._header['nvar'] = unpack(byteorder+'h',
                self._file.read(2))[0]
        if self._header['ds_format'] < 114:
            self._header['nobs'] = unpack(byteorder+'i', self._file.read(4))[0]
        else:
            self._header['nobs'] = unpack(byteorder+'i', self._file.read(4))[0]
        self._header['data_label'] = self._null_terminate(self._file.read(81))
        self._header['time_stamp'] = self._null_terminate(self._file.read(18))

        # parse descriptors
        self._header['typlist'] = [self.TYPE_MAP[ord(self._file.read(1))] \
                for i in range(nvar)]
        self._header['varlist'] = [self._null_terminate(self._file.read(33)) \
                for i in range(nvar)]
        self._header['srtlist'] = unpack(byteorder+('h'*(nvar+1)),
                self._file.read(2*(nvar+1)))[:-1]
        if self._header['ds_format'] <= 113:
            self._header['fmtlist'] = \
                    [self._null_terminate(self._file.read(12)) \
                    for i in range(nvar)]
        else:
            self._header['fmtlist'] = \
                    [self._null_terminate(self._file.read(49)) \
                    for i in range(nvar)]
        self._header['lbllist'] = [self._null_terminate(self._file.read(33)) \
                for i in range(nvar)]
        self._header['vlblist'] = [self._null_terminate(self._file.read(81)) \
                for i in range(nvar)]

        # ignore expansion fields
# When reading, read five bytes; the last four bytes now tell you the size of
# the next read, which you discard.  You then continue like this until you
# read 5 bytes of zeros.
# TODO: The way I read this is that they both should be zero, but that's
# not what we get.

        while True:
            data_type = unpack(byteorder+'b', self._file.read(1))[0]
            data_len = unpack(byteorder+'i', self._file.read(4))[0]
            if data_type == 0:
                break
            self._file.read(data_len)

        # other state vars
        self._data_location = self._file.tell()
        self._has_string_data = len(filter(lambda x: type(x) is int,
            self._header['typlist'])) > 0
        self._col_size()

    def _calcsize(self, fmt):
        return type(fmt) is int and fmt or \
                calcsize(self._header['byteorder']+fmt)

    def _col_size(self, k = None):
        """Calculate size of a data record."""
        if len(self._col_sizes) == 0:
            self._col_sizes = map(lambda x: self._calcsize(x),
                    self._header['typlist'])
        if k == None:
            return self._col_sizes
        else:
            return self._col_sizes[k]

    def _unpack(self, fmt, byt):
        d = unpack(self._header['byteorder']+fmt, byt)[0]
        if fmt[-1] in self.MISSING_VALUES:
            nmin, nmax = self.MISSING_VALUES[fmt[-1]]
            if d < nmin or d > nmax:
                if self._missing_values:
                    return _StataMissingValue(nmax, d)
                else:
                    return None
        return d

    def _next(self):
        typlist = self._header['typlist']
        if self._has_string_data:
            data = [None]*self._header['nvar']
            for i in range(len(data)):
                if type(typlist[i]) is int:
                    data[i] = self._null_terminate(self._file.read(typlist[i]))
                else:
                    data[i] = self._unpack(typlist[i],
                            self._file.read(self._col_size(i)))
            return data
        else:
            return map(lambda i: self._unpack(typlist[i],
                self._file.read(self._col_size(i))),
                range(self._header['nvar']))

def genfromdta(fname, excludelist=None, missing_flt=-999., missing_str=""):
    """
    Returns an ndarray from a Stata .dta file.

    Parameters
    ----------
    fname
    missing_values
    excludelist
    missing_flt
    missing_str

    Notes
    ------
    If the parser encounters a format that it doesn't understand, then it will
    convert to string.  This may be the case with date formats.
    """
#TODO: extend to get data from online
    if isinstance(fname, basestring):
        fhd = StataReader(open(fname, 'r'), missing_values=False)
    elif not hasattr(fname, 'read'):
        raise TypeError("The input should be a string or a filehandle. "\
                "(got %s instead)" % type(fname))
    else:
        fhd = StataReader(fname, missing_values=False)
#    validate_names = np.lib._iotools.NameValidator(excludelist=excludelist,
#                                    deletechars=deletechars,
#                                    case_sensitive=case_sensitive)


#TODO: does this need to handle the byteorder?
    header = fhd.file_headers()
#    types = header['typlist'] # typemap in StataReader?
    nobs = header['nobs']
    numvars = header['nvar']
    varnames = header['varlist']
    dataname = header['data_label']
    labels = header['vlblist'] # labels are thrown away unless DataArray
                               # type is used
    data = np.zeros((nobs,numvars))
    stata_dta = fhd.dataset()

    # build dtype from stata formats
    # see http://www.stata.com/help.cgi?format
    # This converts all of these to float64
    # all time and strings are converted to strings
    #TODO: put these notes in the docstring
    #TODO: need to write a time parser
    to_flt = ['g','e','f','h','gc','fc', 'x', 'l'] # how to deal with x
                                                   # and double-precision
    to_str = ['s']
    if 1:#    if not convert_time: #time parser not written
        to_str.append('t')
    flt_or_str = lambda x: ((x.lower()[-1] in to_str and 's') or \
            (x.lower()[-1] in to_flt and 'f8')) or 's'
    #TODO: this is surely not the best way to handle data types
    convert_missing = {'f8' : missing_flt, 's' : missing_str}
    #TODO: needs to be made more flexible when change types
    fmt = [_.split('.')[-1] for _ in header['fmtlist']]
    remove_comma = [fmt.index(_) for _ in fmt if 'c' in _]
    for i in range(len(fmt)): # remove commas and convert any time types to 't'
        if 't' in fmt[i]:
            fmt[i] = 't'
        if i in remove_comma:
            fmt[i] = fmt[i][:-1] # needs to be changed if time doesn't req.
                                 # loop
    formats = map(flt_or_str, fmt)
# have to go through the whole file first to find string lengths?
#TODO: this is going to be miserably slow
# have a closer look at numpy.genfromtxt and revisit this
    first_list = []
    for rownum,line in enumerate(stata_dta):
        # doesn't handle missing value objects
        # Untested for commas and string missing
        # None will only work without missing value object.
        if None in line and not remove_comma:
            for val in line:
                if val is None:
                    line[line.index(val)] = convert_missing[\
                            formats[line.index(val)]]
        if None in line and remove_comma:
            for i,val in enumerate(line):
                if val is None:
                    line[i] = convert_missing[formats[i]]
                elif i in remove_comma:
                    line[i] = ''.join(line[i].split(','))
                    if formats[i] == 'f8':
                        line[i] = float(line[i])
        if remove_comma and not None in line:
            for j in remove_comma:
                line[j] = ''.join(line[j].split(','))
                if formats[j] == 'f8': # change when change f8
                    line[j] = float(line[j])

        first_list.append(line)
#TODO: add informative error message similar to genfromtxt
# Get string lengths
    strcolidx = []
    if 's' in formats:
        for col,type in enumerate(formats):
            if type == 's':
                strcolidx.append(col)
        for i in strcolidx:
            formats[i] = "a%i" % max(len(str(row[i])) for row in first_list)
    dt = zip(varnames, formats) # make dtype again
    data = np.zeros((nobs), dtype=dt) # init final array
    for i,row in enumerate(first_list):
        data[i] = tuple(row)

#TODO: make it possible to return plain array if all 'f8' for example
    return data

def savetxt(fname, X, names=None, fmt='%.18e', delimiter=' '):
    """
    Save an array to a text file.

    This is just a copy of numpy.savetxt patched to support structured arrays or a
    header of names.  Does not include py3 support now in savetxt.

    Parameters
    ----------
    fname : filename or file handle
        If the filename ends in ``.gz``, the file is automatically saved in
        compressed gzip format.  `loadtxt` understands gzipped files
        transparently.
    X : array_like
        Data to be saved to a text file.
    names : list, optional
        If given names will be the column header in the text file.  If None and
        X is a structured or recarray then the names are taken from X.dtype.names.
    fmt : str or sequence of strs
        A single format (%10.5f), a sequence of formats, or a
        multi-format string, e.g. 'Iteration %d -- %10.5f', in which
        case `delimiter` is ignored.
    delimiter : str
        Character separating columns.

    See Also
    --------
    save : Save an array to a binary file in NumPy ``.npy`` format
    savez : Save several arrays into a ``.npz`` compressed archive

    Notes
    -----
    Further explanation of the `fmt` parameter
    (``%[flag]width[.precision]specifier``):

    flags:
        ``-`` : left justify

        ``+`` : Forces to preceed result with + or -.

        ``0`` : Left pad the number with zeros instead of space (see width).

    width:
        Minimum number of characters to be printed. The value is not truncated
        if it has more characters.

    precision:
        - For integer specifiers (eg. ``d,i,o,x``), the minimum number of
          digits.
        - For ``e, E`` and ``f`` specifiers, the number of digits to print
          after the decimal point.
        - For ``g`` and ``G``, the maximum number of significant digits.
        - For ``s``, the maximum number of characters.

    specifiers:
        ``c`` : character

        ``d`` or ``i`` : signed decimal integer

        ``e`` or ``E`` : scientific notation with ``e`` or ``E``.

        ``f`` : decimal floating point

        ``g,G`` : use the shorter of ``e,E`` or ``f``

        ``o`` : signed octal

        ``s`` : string of characters

        ``u`` : unsigned decimal integer

        ``x,X`` : unsigned hexadecimal integer

    This explanation of ``fmt`` is not complete, for an exhaustive
    specification see [1]_.

    References
    ----------
    .. [1] `Format Specification Mini-Language
           <http://docs.python.org/library/string.html#
           format-specification-mini-language>`_, Python Documentation.

    Examples
    --------
    >>> savetxt('test.out', x, delimiter=',')   # X is an array
    >>> savetxt('test.out', (x,y,z))   # x,y,z equal sized 1D arrays
    >>> savetxt('test.out', x, fmt='%1.4e')   # use exponential notation

    """

    if _is_string_like(fname):
        if fname.endswith('.gz'):
            import gzip
            fh = gzip.open(fname, 'wb')
        else:
            fh = file(fname, 'w')
    elif hasattr(fname, 'seek'):
        fh = fname
    else:
        raise ValueError('fname must be a string or file handle')

    X = np.asarray(X)

    # Handle 1-dimensional arrays
    if X.ndim == 1:
        # Common case -- 1d array of numbers
        if X.dtype.names is None:
            X = np.atleast_2d(X).T
            ncol = 1

        # Complex dtype -- each field indicates a separate column
        else:
            ncol = len(X.dtype.descr)
    else:
        ncol = X.shape[1]

    # `fmt` can be a string with multiple insertion points or a list of formats.
    # E.g. '%10.5f\t%10d' or ('%10.5f', '$10d')
    if type(fmt) in (list, tuple):
        if len(fmt) != ncol:
            raise AttributeError('fmt has wrong shape.  %s' % str(fmt))
        format = delimiter.join(fmt)
    elif type(fmt) is str:
        if fmt.count('%') == 1:
            fmt = [fmt, ]*ncol
            format = delimiter.join(fmt)
        elif fmt.count('%') != ncol:
            raise AttributeError('fmt has wrong number of %% formats.  %s'
                                 % fmt)
        else:
            format = fmt

    # handle names
    if names is None and X.dtype.names:
        names = X.dtype.names

    for row in X:
        if names:
            fh.write(delimiter.join(names) + '\n')
        fh.write(format % tuple(row) + '\n')


if __name__=="__main__":
    try:
        data = genfromdta('./fullauto.dta')
    except:
        raise ImportError, "You don't have the Stata test file downloaded into\
 this directory.  It's not distributed but you can download it here \
http://www.stata-press.com/data/r11/fullauto.dta."
