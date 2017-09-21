class SimpleDoc(object):
    """
    class generating xml/html documents using context managers

    doc, tag, text = SimpleDoc().tagtext()

    with tag('html'):
        with tag('body', id = 'hello'):
            with tag('h1'):
                text('Hello world!')

    print(doc.getvalue())
    """

    class Tag(object):
        def __init__(self, doc, name, attrs):  # name is the tag name (ex: 'div')

            self.doc = doc
            self.name = name
            self.attrs = attrs

        def __enter__(self):
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.position = len(self.doc.result)
            self.doc._append('')

        def __exit__(self, tpe, value, traceback):
            if value is None:
                if self.attrs:
                    self.doc.result[self.position] = "<%s %s>" % (
                        self.name,
                        dict_to_attrs(self.attrs),
                    )
                else:
                    self.doc.result[self.position] = "<%s>" % self.name
                self.doc._append("</%s>" % self.name)
                self.doc.current_tag = self.parent_tag

    class DocumentRoot(object):
        def __getattr__(self, item):
            raise DocError("DocumentRoot here. You can't access anything here.")

    def __init__(self, stag_end=' />'):
        self.result = []
        self.current_tag = self.__class__.DocumentRoot()
        self._append = self.result.append
        assert stag_end in (' />', '/>', '>')
        self._stag_end = stag_end

    def tag(self, tag_name, *args, **kwargs):
        """
        opens a HTML/XML tag for use inside a `with` statement
        the tag is closed when leaving the `with` block
        HTML/XML attributes can be supplied as keyword arguments,
        or alternatively as (key, value) pairs.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)

        In order to supply a "class" html attributes, you must supply a `klass` keyword
        argument. This is because `class` is a reserved python keyword so you can't use it
        outside of a class definition.

        Example::

            with tag('h1', id = 'main-title'):
                text("Hello world!")

            # <h1 id="main-title">Hello world!</h1> was appended to the document

            with tag('td',
                ('data-search', 'lemon'),
                ('data-order', '1384'),
                id = '16'
            ):
                text('Citrus Limon')

            # you get: <td data-search="lemon" data-order="1384" id="16">Citrus Limon</td>


        """
        return self.__class__.Tag(self, tag_name, _attributes(args, kwargs))

    def text(self, *strgs):
        """
        appends 0 or more strings to the document
        the strings are escaped for use as text in html documents, that is,
        & becomes &amp;
        < becomes &lt;
        > becomes &gt;

        Example::

            username = 'Max'
            text('Hello ', username, '!') # appends "Hello Max!" to the current node
            text('16 > 4') # appends "16 &gt; 4" to the current node
        """
        for strg in strgs:
            self._append(html_escape(strg))

    def line(self, tag_name, text_content, *args, **kwargs):
        """
        Shortcut to write tag nodes that contain only text.
        For example, in order to obtain::

            <h1>The 7 secrets of catchy titles</h1>

        you would write::

            line('h1', 'The 7 secrets of catchy titles')

        which is just a shortcut for::

            with tag('h1'):
                text('The 7 secrets of catchy titles')

        The first argument is the tag name, the second argument
        is the text content of the node.
        The optional arguments after that are interpreted as xml/html
        attributes. in the same way as with the `tag` method.

        Example::

            line('a', 'Who are we?', href = '/about-us.html')

        produces::

            <a href="/about-us.html">Who are we?</a>
        """
        with self.tag(tag_name, *args, **kwargs):
            self.text(text_content)

    def asis(self, *strgs):
        """
        appends 0 or more strings to the documents
        contrary to the `text` method, the strings are appended "as is"
        &, < and > are NOT escaped

        Example::

            doc.asis('<!DOCTYPE html>') # appends <!DOCTYPE html> to the document
        """
        for strg in strgs:
            if strg is None:
                raise TypeError("Expected a string, got None instead.")
                # passing None by mistake was frequent enough to justify a check
                # see https://github.com/leforestier/yattag/issues/20
            self._append(strg)

    def nl(self):
        self._append('\n')

    def attr(self, *args, **kwargs):
        """
        sets HTML/XML attribute(s) on the current tag
        HTML/XML attributes are supplied as (key, value) pairs of strings,
        or as keyword arguments.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)
        Note that, instead, you can set html/xml attributes by passing them as
        keyword arguments to the `tag` method.

        In order to supply a "class" html attributes, you can either pass
        a ('class', 'my_value') pair, or supply a `klass` keyword argument
        (this is because `class` is a reserved python keyword so you can't use it
        outside of a class definition).

        Examples::

            with tag('h1'):
                text('Welcome!')
                doc.attr(id = 'welcome-message', klass = 'main-title')

            # you get: <h1 id="welcome-message" class="main-title">Welcome!</h1>

            with tag('td'):
                text('Citrus Limon')
                doc.attr(
                    ('data-search', 'lemon'),
                    ('data-order', '1384')
                )


            # you get: <td data-search="lemon" data-order="1384">Citrus Limon</td>

        """
        self.current_tag.attrs.update(_attributes(args, kwargs))

    def stag(self, tag_name, *args, **kwargs):
        """
        appends a self closing tag to the document
        html/xml attributes can be supplied as keyword arguments,
        or alternatively as (key, value) pairs.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)

        Example::

            doc.stag('img', src = '/salmon-plays-piano.jpg')
            # appends <img src="/salmon-plays-piano.jpg" /> to the document

        If you want to produce self closing tags without the ending slash (HTML5 style),
        use the stag_end parameter of the SimpleDoc constructor at the creation of the
        SimpleDoc instance.

        Example::

            >>> doc = SimpleDoc(stag_end = '>')
            >>> doc.stag('br')
            >>> doc.getvalue()
            '<br>'
        """
        if args or kwargs:
            self._append("<%s %s%s" % (
                tag_name,
                dict_to_attrs(_attributes(args, kwargs)),
                self._stag_end
            ))
        else:
            self._append("<%s%s" % (tag_name, self._stag_end))

    def cdata(self, strg, safe=False):
        """
        appends a CDATA section containing the supplied string

        You don't have to worry about potential ']]>' sequences that would terminate
        the CDATA section. They are replaced with ']]]]><![CDATA[>'.

        If you're sure your string does not contain ']]>', you can pass `safe = True`.
        If you do that, your string won't be searched for ']]>' sequences.
        """
        self._append('<![CDATA[')
        if safe:
            self._append(strg)
        else:
            self._append(strg.replace(']]>', ']]]]><![CDATA[>'))
        self._append(']]>')

    def getvalue(self):
        """
        returns the whole document as a single string
        """
        return ''.join(self.result)

    def tagtext(self):
        """
        return a triplet composed of::
            . the document itself
            . its tag method
            . its text method

        Example::

            doc, tag, text = SimpleDoc().tagtext()

            with tag('h1'):
                text('Hello world!')

            print(doc.getvalue()) # prints <h1>Hello world!</h1>
        """

        return self, self.tag, self.text

    def ttl(self):
        """
        returns a quadruplet composed of::
            . the document itself
            . its tag method
            . its text method
            . its line method

        Example::

            doc, tag, text, line = SimpleDoc().ttl()

            with tag('ul', id='grocery-list'):
                line('li', 'Tomato sauce', klass="priority")
                line('li', 'Salt')
                line('li', 'Pepper')

            print(doc.getvalue())
        """
        return self, self.tag, self.text, self.line

    def add_class(self, *classes):
        """
        adds one or many elements to the html "class" attribute of the current tag
        Example::
            user_logged_in = False
            with tag('a', href="/nuclear-device", klass = 'small'):
                if not user_logged_in:
                    doc.add_class('restricted-area')
                text("Our new product")

            print(doc.getvalue())

            # prints <a class="restricted-area small" href="/nuclear-device"></a>
        """
        self._set_classes(
            self._get_classes().union(classes)
        )

    def discard_class(self, *classes):
        """
        remove one or many elements from the html "class" attribute of the current
        tag if they are present (do nothing if they are absent)
        """
        self._set_classes(
            self._get_classes().difference(classes)
        )

    def toggle_class(self, elem, active):
        """
        if active is a truthy value, ensure elem is present inside the html
        "class" attribute of the current tag, otherwise (if active is falsy)
        ensure elem is absent
        """
        classes = self._get_classes()
        if active:
            classes.add(elem)
        else:
            classes.discard(elem)
        self._set_classes(classes)

    def _get_classes(self):
        try:
            current_classes = self.current_tag.attrs['class']
        except KeyError:
            return set()
        else:
            return set(current_classes.split())

    def _set_classes(self, classes_set):
        if classes_set:
            self.current_tag.attrs['class'] = ' '.join(classes_set)
        else:
            try:
                del self.current_tag.attrs['class']
            except KeyError:
                pass


class DocError(Exception):
    pass


def html_escape(s):
    if isinstance(s, (int, float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    except AttributeError:
        raise TypeError(
            "You can only insert a string, an int or a float inside a xml/html text node. "
            "Got %s (type %s) instead." % (repr(s), repr(type(s)))
        )


def attr_escape(s):
    if isinstance(s, (int, float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    except AttributeError:
        raise TypeError(
            "xml/html attributes should be passed as strings, ints or floats. "
            "Got %s (type %s) instead." % (repr(s), repr(type(s)))
        )


ATTR_NO_VALUE = object()


def dict_to_attrs(dct):
    return ' '.join(
        (key if value is ATTR_NO_VALUE
         else '%s="%s"' % (key, attr_escape(value)))
        for key, value in dct.items()
    )


def _attributes(args, kwargs):
    lst = []
    for arg in args:
        if isinstance(arg, tuple):
            lst.append(arg)
        elif isinstance(arg, str):
            lst.append((arg, ATTR_NO_VALUE))
        else:
            raise ValueError(
                "Couldn't make a XML or HTML attribute/value pair out of %s."
                % repr(arg)
            )
    result = dict(lst)
    result.update(
        (('class', value) if key == 'klass' else (key, value))
        for key, value in kwargs.items()
    )
    return result


import re

__all__ = ['indent']


class TokenMeta(type):
    _token_classes = {}

    def __new__(cls, name, bases, attrs):
        kls = type.__new__(cls, name, bases, attrs)
        cls._token_classes[name] = kls
        return kls

    @classmethod
    def getclass(cls, name):
        return cls._token_classes[name]


# need to proceed that way for Python 2/3 compatility:
TokenBase = TokenMeta('TokenBase', (object,), {})


class Token(TokenBase):
    regex = None

    def __init__(self, groupdict):
        self.content = groupdict[self.__class__.__name__]


class Text(Token):
    regex = '[^<>]+'

    def __init__(self, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        self._isblank = None

    @property
    def isblank(self):
        if self._isblank is None:
            self._isblank = not self.content.strip()
        return self._isblank


class Comment(Token):
    regex = r'<!--((?!-->).)*.?-->'


class CData(Token):
    regex = r'<!\[CDATA\[((?!\]\]>).*).?\]\]>'


class Doctype(Token):
    regex = r'''<!DOCTYPE(\s+([^<>"']+|"[^"]*"|'[^']*'))*>'''


_open_tag_start = r'''
    <\s*
        (?P<{tag_name_key}>{tag_name_rgx})
        (\s+[^/><"=\s]+     # attribute
            (\s*=\s*
                (
                    [^/><"=\s]+ |    # unquoted attribute value
                    ("[^"]*") |    # " quoted attribute value
                    ('[^']*')      # ' quoted attribute value
                )
            )?  # the attribute value is optional (we're forgiving)
        )*
    \s*'''


class Script(Token):
    _end_script = r'<\s*/\s*script\s*>'

    regex = _open_tag_start.format(
        tag_name_key='script_ignore',
        tag_name_rgx='script',
    ) + r'>((?!({end_script})).)*.?{end_script}'.format(
        end_script=_end_script
    )


class Style(Token):
    _end_style = r'<\s*/\s*style\s*>'

    regex = _open_tag_start.format(
        tag_name_key='style_ignore',
        tag_name_rgx='style',
    ) + r'>((?!({end_style})).)*.?{end_style}'.format(
        end_style=_end_style
    )


class XMLDeclaration(Token):
    regex = _open_tag_start.format(
        tag_name_key='xmldecl_ignore',
        tag_name_rgx=r'\?\s*xml'
    ) + r'\?\s*>'


class NamedTagTokenMeta(TokenMeta):
    def __new__(cls, name, bases, attrs):
        kls = TokenMeta.__new__(cls, name, bases, attrs)
        if name not in ('NamedTagTokenBase', 'NamedTagToken'):
            kls.tag_name_key = 'tag_name_%s' % name
            kls.regex = kls.regex_template.format(
                tag_name_key=kls.tag_name_key,
                tag_name_rgx=kls.tag_name_rgx
            )
        return kls


# need to proceed that way for Python 2/3 compatility
NamedTagTokenBase = NamedTagTokenMeta(
    'NamedTagTokenBase',
    (Token,),
    {'tag_name_rgx': r'[^/><"\s]+'}
)


class NamedTagToken(NamedTagTokenBase):
    def __init__(self, groupdict):
        super(NamedTagToken, self).__init__(groupdict)
        self.tag_name = groupdict[self.__class__.tag_name_key]


class OpenTag(NamedTagToken):
    regex_template = _open_tag_start + '>'


class SelfTag(NamedTagToken):  # a self closing tag
    regex_template = _open_tag_start + r'/\s*>'


class CloseTag(NamedTagToken):
    regex_template = r'<\s*/(?P<{tag_name_key}>{tag_name_rgx})(\s[^/><"]*)?>'


class XMLTokenError(Exception):
    pass


class Tokenizer(object):
    def __init__(self, token_classes):
        self.token_classes = token_classes
        self.token_names = [kls.__name__ for kls in token_classes]
        self.get_token = None

    def _compile_regex(self):
        self.get_token = re.compile(
            '|'.join(
                '(?P<%s>%s)' % (klass.__name__, klass.regex) for klass in self.token_classes
            ),
            re.X | re.I | re.S
        ).match

    def tokenize(self, string):
        if not self.get_token:
            self._compile_regex()
        result = []
        append = result.append
        while string:
            mobj = self.get_token(string)
            if mobj:
                groupdict = mobj.groupdict()
                class_name = next(name for name in self.token_names if groupdict[name])
                token = TokenMeta.getclass(class_name)(groupdict)
                append(token)
                string = string[len(token.content):]
            else:
                raise XMLTokenError("Unrecognized XML token near %s" % repr(string[:100]))

        return result


tokenize = Tokenizer(
    (Text, Comment, CData, Doctype, XMLDeclaration, Script, Style, OpenTag, SelfTag, CloseTag)
).tokenize


class TagMatcher(object):
    class SameNameMatcher(object):
        def __init__(self):
            self.unmatched_open = []
            self.matched = {}

        def sigclose(self, i):
            if self.unmatched_open:
                open_tag = self.unmatched_open.pop()
                self.matched[open_tag] = i
                self.matched[i] = open_tag
                return open_tag
            else:
                return None

        def sigopen(self, i):
            self.unmatched_open.append(i)

    def __init__(self, token_list, blank_is_text=False):
        self.token_list = token_list
        self.name_matchers = {}
        self.direct_text_parents = set()

        for i in range(len(token_list)):
            token = token_list[i]
            tpe = type(token)
            if tpe is OpenTag:
                self._get_name_matcher(token.tag_name).sigopen(i)
            elif tpe is CloseTag:
                self._get_name_matcher(token.tag_name).sigclose(i)

        # TODO move this somewhere else
        current_nodes = []
        for i in range(len(token_list)):
            token = token_list[i]
            tpe = type(token)
            if tpe is OpenTag and self.ismatched(i):
                current_nodes.append(i)
            elif tpe is CloseTag and self.ismatched(i):
                current_nodes.pop()
            elif tpe is Text and (blank_is_text or not token.isblank):
                if current_nodes:
                    self.direct_text_parents.add(current_nodes[-1])

    def _get_name_matcher(self, tag_name):
        try:
            return self.name_matchers[tag_name]
        except KeyError:
            self.name_matchers[tag_name] = name_matcher = self.__class__.SameNameMatcher()
            return name_matcher

    def ismatched(self, i):
        return i in self.name_matchers[self.token_list[i].tag_name].matched

    def directly_contains_text(self, i):
        return i in self.direct_text_parents


def indent(string, indentation='  ', newline='\n', indent_text=False, blank_is_text=False):
    """
    takes a string representing a html or xml document and returns
     a well indented version of it

    arguments:
    - string: the string to process
    - indentation: the indentation unit (default to two spaces)
    - newline: the string to be use for new lines
      (default to  '\\n', could be set to '\\r\\n' for example)
    - indent_text:

        if True, text nodes will be indented:

            <p>Hello</p>

            would result in

            <p>
                hello
            </p>

        if False, text nodes won't be indented, and the content
         of any node directly containing text will be unchanged:

            <p>Hello</p> will be unchanged

            <p><strong>Hello</strong> world!</p> will be unchanged
             since ' world!' is directly contained in the <p> node.

            This is the default since that's generally what you want for HTML.

    - blank_is_text:
        if False, completely blank texts are ignored. That is the default.
    """
    tokens = tokenize(string)
    tag_matcher = TagMatcher(tokens, blank_is_text=blank_is_text)
    ismatched = tag_matcher.ismatched
    directly_contains_text = tag_matcher.directly_contains_text
    result = []
    append = result.append
    level = 0
    sameline = 0
    was_just_opened = False
    tag_appeared = False

    def _indent():
        if tag_appeared:
            append(newline)
        for i in range(level):
            append(indentation)

    for i, token in enumerate(tokens):
        tpe = type(token)
        if tpe is Text:
            if blank_is_text or not token.isblank:
                if not sameline:
                    _indent()
                append(token.content)
                was_just_opened = False
        elif tpe is OpenTag and ismatched(i):
            was_just_opened = True
            if sameline:
                sameline += 1
            else:
                _indent()
            if not indent_text and directly_contains_text(i):
                sameline = sameline or 1
            append(token.content)
            level += 1
            tag_appeared = True
        elif tpe is CloseTag and ismatched(i):
            level -= 1
            tag_appeared = True
            if sameline:
                sameline -= 1
            elif not was_just_opened:
                _indent()
            append(token.content)
            was_just_opened = False
        else:
            if not sameline:
                _indent()
            append(token.content)
            was_just_opened = False
            tag_appeared = True
    return ''.join(result)


if __name__ == '__main__':
    import sys

    print(indent(sys.stdin.read()))

try:
    range = xrange  # for Python 2/3 compatibility
except NameError:
    pass

__all__ = ['Doc']


class SimpleInput(object):
    """
    class representing text inputs, password inputs, hidden inputs etc...
    """

    def __init__(self, name, tpe, attrs):
        self.name = name
        self.tpe = tpe
        self.attrs = attrs

    def render(self, defaults, errors, error_wrapper, stag_end=' />'):
        lst = []
        attrs = dict(self.attrs)
        error = errors and self.name in errors
        if error:
            _add_class(attrs, 'error')
            lst.append(error_wrapper[0])
            lst.append(html_escape(errors[self.name]))
            lst.append(error_wrapper[1])

        if self.name in defaults:
            attrs['value'] = str(defaults[self.name])
        attrs['name'] = self.name
        lst.append('<input type="%s" %s%s' % (self.tpe, dict_to_attrs(attrs), stag_end))

        return ''.join(lst)


class CheckableInput(object):
    tpe = 'checkbox'

    def __init__(self, name, attrs):
        self.name = name
        self.rank = 0
        self.attrs = attrs

    def setrank(self, n):
        self.rank = n

    @classmethod
    def match(cls, default, value):
        if isinstance(default, str):
            return value == default
        elif isinstance(default, (tuple, list, set)):
            return value in default
        return False

    def checked(self, defaults):
        try:
            default = defaults[self.name]
        except KeyError:
            return False
        try:
            value = self.attrs['value']
        except KeyError:
            return False
        return self.__class__.match(default, value)

    def render(self, defaults, errors, error_wrapper, stag_end=' />'):
        lst = []
        attrs = dict(self.attrs)
        if self.rank == 0:
            if errors and self.name in errors:
                lst.append(error_wrapper[0])
                lst.append(html_escape(errors[self.name]))
                lst.append(error_wrapper[1])
                _add_class(attrs, 'error')

        if self.checked(defaults):
            attrs['checked'] = 'checked'

        attrs['name'] = self.name

        lst.append('<input type="%s" %s%s' % (self.__class__.tpe, dict_to_attrs(attrs), stag_end))

        return ''.join(lst)


class CheckboxInput(CheckableInput):
    pass


class RadioInput(CheckableInput):
    tpe = 'radio'

    @classmethod
    def match(cls, default, value):
        if isinstance(default, str):
            return value == default
        return False


def groupclass(inputclass):
    class InputGroup(object):
        def __init__(self, name):
            self.name = name
            self.n_items = 0

        def input(self, attrs):
            input_instance = inputclass(self.name, attrs)
            input_instance.setrank(self.n_items)
            self.n_items += 1
            return input_instance

    return InputGroup


class ContainerTag(object):
    tag_name = 'textarea'

    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    def render(self, defaults, errors, error_wrapper, inner_content=''):
        lst = []
        attrs = dict(self.attrs)
        if errors and self.name in errors:
            lst.append(error_wrapper[0])
            lst.append(html_escape(errors[self.name]))
            lst.append(error_wrapper[1])
            _add_class(attrs, 'error')
        attrs['name'] = self.name

        lst.append('<%s %s>' % (self.__class__.tag_name, dict_to_attrs(attrs)))
        if self.name in defaults:
            lst.append(html_escape(str(defaults[self.name])))
        else:
            lst.append(inner_content)

        lst.append('</%s>' % self.__class__.tag_name)

        return ''.join(lst)


class Textarea(ContainerTag):
    pass


class Select(ContainerTag):
    tag_name = 'select'


class Option(object):
    def __init__(self, name, multiple, value, attrs):
        self.name = name
        self.multiple = multiple
        self.value = value
        self.attrs = attrs

    def render(self, defaults, errors, inner_content):
        selected = False
        if self.name in defaults:
            if self.multiple:
                if self.value in defaults[self.name]:
                    selected = True
            else:
                if self.value == defaults[self.name]:
                    selected = True
        lst = ['<option value="', attr_escape(self.value), '"']
        if selected:
            lst.append(' selected="selected"')
        if self.attrs:
            lst.append(' ')
            lst.append(dict_to_attrs(self.attrs))
        lst.append('>')
        lst.append(inner_content)
        lst.append('</option>')
        return ''.join(lst)


def _attrs_from_args(required_keys, *args, **kwargs):
    # need to do all this to allow specifying attributes as (key, value) pairs
    # while maintaining backward compatibility with previous versions
    # of yattag, which allowed 'name', 'type', and 'value' attributes
    # as positional or as keyword arguments
    def raise_exception(arg):
        raise ValueError(
            "Optional attributes should be passed as (key, value) pairs or as keyword arguments."
            "Got %s (type %s)" % (repr(arg), repr(type(arg)))
        )

    limit = 0
    for arg in args:
        if isinstance(arg, tuple):
            break
        else:
            limit += 1
    if limit > len(required_keys):
        raise_exception(args[limit - 1])
    attrs = dict(zip(required_keys[:limit], args[:limit]))
    for arg in args[limit:]:
        if isinstance(arg, tuple):
            attrs[arg[0]] = arg[1]
        else:
            raise_exception(arg)
    attrs.update(
        (('class', value) if key == 'klass' else (key, value))
        for key, value in kwargs.items()
    )

    required_attrs = []

    for key in required_keys:
        try:
            required_attrs.append(attrs.pop(key))
        except KeyError:
            raise ValueError(
                "the %s attribute is missing" % repr(key)
            )
    return required_attrs + [attrs]


class Doc(SimpleDoc):
    """
    The Doc class extends the SimpleDoc class with form rendering capabilities.
    Pass default values or errors as dictionnaries to the Doc constructor, and
    use the `input`, `textarea`, `select`, `option` methods
    to append form elements to the document.
    """

    SimpleInput = SimpleInput
    CheckboxInput = CheckboxInput
    RadioInput = RadioInput
    Textarea = Textarea
    Select = Select
    Option = Option

    class TextareaTag(object):
        def __init__(self, doc, name, attrs):
            # name is the name attribute of the textarea, ex: 'contact_message'
            # for <textarea name="contact_message">
            self.doc = doc
            self.name = name
            self.attrs = attrs

        def __enter__(self):
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.position = len(self.doc.result)
            self.doc._append('')

        def __exit__(self, tpe, value, traceback):
            if value is None:
                inner_content = ''.join(self.doc.result[self.position + 1:])
                del self.doc.result[self.position + 1:]
                rendered_textarea = self.doc.__class__.Textarea(self.name, self.attrs).render(
                    defaults=self.doc.defaults,
                    errors=self.doc.errors,
                    inner_content=inner_content,
                    error_wrapper=self.doc.error_wrapper
                )
                self.doc.result[self.position] = rendered_textarea
                self.doc.current_tag = self.parent_tag

    class SelectTag(object):
        def __init__(self, doc, name, attrs):
            # name is the name attribute of the select, ex: 'color'
            # for <select name="color">
            self.doc = doc
            self.name = name
            self.attrs = attrs
            self.multiple = bool(attrs.get('multiple'))
            self.old_current_select = None

        def __enter__(self):
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.position = len(self.doc.result)
            self.doc._append('')
            self.old_current_select = self.doc.current_select
            self.doc.current_select = self

        def __exit__(self, tpe, value, traceback):
            if value is None:
                inner_content = ''.join(self.doc.result[self.position + 1:])
                del self.doc.result[self.position + 1:]
                rendered_select = self.doc.__class__.Select(self.name, self.attrs).render(
                    defaults={},
                    # no defaults for the <select> tag. Defaults are handled by the <option> tags directly.
                    errors=self.doc.errors,
                    inner_content=inner_content,
                    error_wrapper=self.doc.error_wrapper
                )
                self.doc.result[self.position] = rendered_select
                self.doc.current_tag = self.parent_tag
                self.doc.current_select = self.old_current_select

    class OptionTag(object):
        def __init__(self, doc, select, value, attrs):
            self.doc = doc
            self.select = select
            self.attrs = attrs
            self.value = value

        def __enter__(self):
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.position = len(self.doc.result)
            self.doc._append('')

        def __exit__(self, tpe, value, traceback):
            if value is None:
                inner_content = ''.join(self.doc.result[self.position + 1:])
                del self.doc.result[self.position + 1:]
                self.doc.result[self.position] = self.doc.__class__.Option(
                    name=self.select.name,
                    multiple=self.select.multiple,
                    value=self.value,
                    attrs=self.attrs
                ).render(
                    defaults=self.doc.defaults,
                    errors=self.doc.errors,
                    inner_content=inner_content
                )
                self.doc.current_tag = self.parent_tag

    def __init__(self, defaults=None, errors=None,
                 error_wrapper=('<span class="error">', '</span>'), *args, **kwargs):
        """
        creates a Doc instance

        defaults::
            optional dictionnary of values used to fill html forms
        errors::
            optional dictionnary of errors used to fill html forms

        Example 1::
            doc = Doc()

        Example 2::
            doc = Doc(
                defaults = {
                    'beverage': 'coffee',
                    'preferences': ['milk', 'sugar'],
                    'use_discount': True
                },
                errors = {
                    'preferences': "We ran out of milk!"
                }
            )

        Note: very often you'll want to call the `tagtext` method just after
        creating a Doc instance. Like this::

        doc, tag, text = Doc(defaults = {'color': 'blue'}).tagtext()

        This way, you can write `tag` (resp. `text`) in place of `doc.tag`
        (resp. `doc.text`). When writing long html templates or xml documents,
        it's a gain in readability and performance.
        """

        super(Doc, self).__init__(*args, **kwargs)
        self.defaults = defaults or {}
        self.errors = errors or {}
        self.error_wrapper = error_wrapper
        self.radios = {}
        self.checkboxes = {}
        self.current_select = None
        self.radio_group_class = groupclass(self.__class__.RadioInput)
        self.checkbox_group_class = groupclass(self.__class__.CheckboxInput)
        self._fields = set()
        self._detached_errors_pos = []

    def input(self, *args, **kwargs):
        "required attributes: 'name' and 'type'"
        name, type, attrs = _attrs_from_args(('name', 'type'), *args, **kwargs)
        self._fields.add(name)
        if type in (
                'text', 'password', 'hidden', 'search', 'email', 'url', 'number',
                'range', 'date', 'datetime', 'datetime-local', 'month', 'week',
                'time', 'color'
        ):
            self.asis(
                self.__class__.SimpleInput(name, type, attrs).render(
                    self.defaults, self.errors, self.error_wrapper, self._stag_end
                )
            )
            return
        if type == 'radio':
            if name not in self.radios:
                self.radios[name] = self.radio_group_class(name)
            checkable_group = self.radios[name]
        elif type == 'checkbox':
            if name not in self.checkboxes:
                self.checkboxes[name] = self.checkbox_group_class(name)
            checkable_group = self.checkboxes[name]
        else:
            if type == 'submit':
                raise DocError(
                    "Unhandled input type: submit. Use doc.stag('input', type = 'submit', value='whatever') instead.")
            else:
                raise DocError("Unknown input type: %s" % type)

        self._append(
            checkable_group.input(attrs).render(self.defaults, self.errors, self.error_wrapper, self._stag_end))

    def textarea(self, *args, **kwargs):
        "required attribute: 'name'"
        name, attrs = _attrs_from_args(('name',), *args, **kwargs)
        self._fields.add(name)
        return self.__class__.TextareaTag(self, name, attrs)

    def select(self, *args, **kwargs):
        "required attribute: 'name'"
        name, attrs = _attrs_from_args(('name',), *args, **kwargs)
        self._fields.add(name)
        return self.__class__.SelectTag(self, name, attrs)

    def option(self, *args, **kwargs):
        "required attribute: 'value'"
        if self.current_select:
            value, attrs = _attrs_from_args(('value',), *args, **kwargs)
            return self.__class__.OptionTag(self, self.current_select, value, attrs)
        else:
            raise DocError("No <select> tag opened. Can't put an <option> here.")

    def detached_errors(self, render_function=None):
        self._detached_errors_pos.append((len(self.result), render_function or self.error_dict_to_string))
        self.result.append('')

    def error_dict_to_string(self, dct):
        if dct:
            doc, tag, text = SimpleDoc().tagtext()
            with tag('ul', klass='error-list'):
                for error in dct.values():
                    with tag('li'):
                        text(error)
            return doc.getvalue()
        else:
            return ''

    def getvalue(self):
        """
        returns the whole document as a string
        """
        for position, render_function in self._detached_errors_pos:
            self.result[position] = render_function(
                dict((name, self.errors[name]) for name in self.errors if name not in self._fields)
            )
        return ''.join(self.result)


def _add_class(dct, klass):
    classes = dct.get('class', '').split()
    if klass not in classes:
        dct['class'] = ' '.join(classes + [klass])
