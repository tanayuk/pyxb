"""This file contains support classes from which schema-specific
bindings inherit, and that describe the content models of those
schema."""

from pywxsb.exceptions_ import *
import xml.dom as dom
from xml.dom import minidom
import pywxsb.utils.domutils as domutils
import pywxsb.utils.utility as utility
import types
import pywxsb.Namespace

class simpleTypeDefinition (utility._DeconflictSymbols_mixin, object):
    """simpleTypeDefinition is a base mix-in class that is part of the hierarchy
    of any class that represents the Python datatype for a
    SimpleTypeDefinition.

    Note: This class, or a descendent of it, must be the first class
    in the method resolution order when a subclass has multiple
    parents.  Otherwise, constructor keyword arguments may not be
    removed before passing them on to Python classes that do not
    accept them.
    """

    # A map from leaf classes in the facets module to instance of
    # those classes that constrain or otherwise affect the datatype.
    # Note that each descendent of simpleTypeDefinition has its own map.
    __FacetMap = {}

    # Symbols that remain the responsibility of this class.  Any
    # public symbols in generated binding subclasses are deconflicted
    # by providing an alternative name in the subclass.  (There
    # currently are no public symbols in generated SimpleTypeDefinion
    # bindings.)
    _ReservedSymbols = set([ 'Factory', 'CreateFromDOM', 'XsdLiteral', 'xsdLiteral',
                            'XsdSuperType', 'XsdPythonType', 'XsdConstraintsOK',
                            'xsdConstraintsOK', 'XsdValueLength', 'xsdValueLength',
                            'PythonLiteral', 'pythonLiteral', 'toDOM' ])

    # Determine the name of the class-private facet map.  This
    # algorithm should match the one used by Python, so the base class
    # value can be read.
    @classmethod
    def __FacetMapAttributeName (cls):
        return '_%s__FacetMap' % (cls.__name__.strip('_'),)

    @classmethod
    def _FacetMap (cls):
        """Return a reference to the facet map for this datatype.

        The facet map is a map from leaf facet classes to instances of
        those classes that constrain or otherwise apply to the lexical
        or value space of the datatype.

        Raises AttributeError if the facet map has not been defined."""
        return getattr(cls, cls.__FacetMapAttributeName())
    
    @classmethod
    def _InitializeFacetMap (cls, *args):
        """Initialize the facet map for this datatype.

        This must be called exactly once, after all facets belonging
        to the datatype have been created.

        Raises LogicError if called multiple times, or if called when
        a parent class facet map has not been initialized."""
        fm = None
        try:
            fm = cls._FacetMap()
        except AttributeError:
            pass
        if fm is not None:
            raise LogicError('%s facet map initialized multiple times' % (cls.__name__,))
        for super_class in cls.mro()[1:]:
            if issubclass(super_class, simpleTypeDefinition):
                fm = super_class._FacetMap()
                break
        if fm is None:
            raise LogicError('%s is not a child of simpleTypeDefinition' % (cls.__name__,))
        fm = fm.copy()
        for facet in args:
            fm[type(facet)] = facet
        setattr(cls, cls.__FacetMapAttributeName(), fm)
        return fm

    @classmethod
    def __ConvertArgs (cls, args):
        """If the first argument is a string, and this class has a
        whitespace facet, replace the first argument with the results
        of applying whitespace normalization.

        We need to do this for both __new__ and __init__, because in
        some cases (e.g., str/unicode) the value is assigned during
        __new__ not __init__."""
        if (0 < len(args)) and isinstance(args[0], types.StringTypes):
            cf_whitespace = getattr(cls, '_CF_whiteSpace', None)
            if cf_whitespace is not None:
                norm_str = unicode(cf_whitespace.normalizeString(args[0]))
                args = (norm_str,) + args[1:]
        return args

    @classmethod
    def Factory (cls, *args, **kw):
        """Provide a common mechanism to create new instances of this type.

        The class constructor won't do, because you can't create
        instances of union types.

        This method may be overridden in subclasses (like STD_union)."""
        return cls(*args, **kw)

    @classmethod
    def CreateFromDOM (cls, node):
        """Create a simple type instance from the given DOM Node instance."""
        # @todo error if non-text content?
        return cls.Factory(domutils.ExtractTextContent(node))

    # Must override new, because new gets invoked before init, and
    # usually doesn't accept keywords.  In case it does, only remove
    # the ones that are interpreted by this class.  Do the same
    # argument conversion as is done in init.
    def __new__ (cls, *args, **kw):
        kw.pop('validate_constraints', None)
        return super(simpleTypeDefinition, cls).__new__(cls, *cls.__ConvertArgs(args), **kw)

    # Validate the constraints after invoking the parent constructor,
    # unless told not to.
    def __init__ (self, *args, **kw):
        validate_constraints = kw.pop('validate_constraints', True)
        super(simpleTypeDefinition, self).__init__(*self.__ConvertArgs(args), **kw)
        if validate_constraints:
            self.xsdConstraintsOK()

    # This is a placeholder for a class method that will retrieve the
    # set of facets associated with the class.  We can't define it
    # here because the facets module has a dependency on this module.
    _GetConstrainingFacets = None

    # The class attribute name used to store the reference to the STD
    # instance must be unique to the class, not to this base class.
    # Otherwise we mistakenly believe we've already associated a STD
    # instance with a class (e.g., xsd:normalizedString) when in fact it's
    # associated with the superclass (e.g., xsd:string)
    @classmethod
    def __STDAttrName (cls):
        return '_%s__SimpleTypeDefinition' % (cls.__name__,)

    @classmethod
    def _SimpleTypeDefinition (cls, std):
        attr_name = cls.__STDAttrName()
        if hasattr(cls, attr_name):
            old_value = getattr(cls, attr_name)
            if old_value != std:
                raise LogicError('%s: Attempt to override existing STD %s with %s' % (cls, old_value.name(), std.name()))
        setattr(cls, attr_name, std)

    @classmethod
    def SimpleTypeDefinition (cls):
        """Return the SimpleTypeDefinition instance for the given
        class.  This should only be invoked when generating bindings.
        Raise IncompleteImplementationError if no STD instance has
        been associated with the class."""
        attr_name = cls.__STDAttrName()
        if hasattr(cls, attr_name):
            return getattr(cls, attr_name)
        raise IncompleteImplementationError('%s: No STD available' % (cls,))

    @classmethod
    def XsdLiteral (cls, value):
        """Convert from a python value to a string usable in an XML
        document."""
        raise LogicError('%s does not implement XsdLiteral' % (cls,))

    def xsdLiteral (self):
        """Return text suitable for representing the value of this
        instance in an XML document."""
        return self.XsdLiteral(self)

    @classmethod
    def XsdSuperType (cls):
        """Find the nearest parent class in the PST hierarchy.

        The value for anySimpleType is None; for all others, it's a
        primitive or derived PST descendent (including anySimpleType)."""
        for sc in cls.mro():
            if sc == cls:
                continue
            if simpleTypeDefinition == sc:
                # If we hit the PST base, this is a primitive type or
                # otherwise directly descends from a Python type; return
                # the recorded XSD supertype.
                return cls._XsdBaseType
            if issubclass(sc, simpleTypeDefinition):
                return sc
        raise LogicError('No supertype found for %s' % (cls,))

    @classmethod
    def XsdPythonType (cls):
        """Find the first parent class that isn't part of the
        PST_mixin hierarchy.  This is expected to be the Python value
        class."""
        for sc in cls.mro():
            if sc == object:
                continue
            if not issubclass(sc, simpleTypeDefinition):
                return sc
        raise LogicError('No python type found for %s' % (cls,))

    @classmethod
    def _XsdConstraintsPreCheck_vb (cls, value):
        """Pre-extended class method to verify other things before checking constraints."""
        super_fn = getattr(super(simpleTypeDefinition, cls), '_XsdConstraintsPreCheck_vb', lambda *a,**kw: True)
        return super_fn(value)

    @classmethod
    def XsdConstraintsOK (cls, value):
        """Validate the given value against the constraints on this class.

        Throws BadTypeValueError if any constraint is violated.
        """

        cls._XsdConstraintsPreCheck_vb(value)

        facet_values = None

        # When setting up the datatypes, if we attempt to validate
        # something before the facets have been initialized (e.g., a
        # nonNegativeInteger used as a length facet for the parent
        # integer datatype), just ignore that.
        try:
            facet_values = cls._FacetMap().values()
        except AttributeError:
            return value
        for f in facet_values:
            if not f.validateConstraint(value):
                raise BadTypeValueError('%s violation for %s in %s' % (f.Name(), value, cls.__name__))
            #print '%s ok for %s' % (f.Name(), value)
        return value

    def xsdConstraintsOK (self):
        """Validate the value of this instance against its constraints."""
        return self.XsdConstraintsOK(self)

    @classmethod
    def XsdValueLength (cls, value):
        """Return the length of the given value.

        The length is calculated by a subclass implementation of
        _XsdValueLength_vx in accordance with
        http://www.w3.org/TR/xmlschema-2/#rf-length.

        The return value is a non-negative integer, or None if length
        constraints should be considered trivially satisfied (as with
        QName and NOTATION).

        Raise LogicError if the provided value is not an instance of cls.

        Raise LogicError if an attempt is made to calculate a length
        for an instance of a type that does not support length
        calculations.
        """
        assert isinstance(value, cls)
        if not hasattr(cls, '_XsdValueLength_vx'):
            raise LogicError('Class %s does not support length validation' % (cls.__name__,))
        return cls._XsdValueLength_vx(value)

    def xsdValueLength (self):
        """Return the length of this instance within its value space.
        See XsdValueLength."""
        return self.XsdValueLength(self)

    @classmethod
    def PythonLiteral (cls, value):
        """Return a string which can be embedded into Python source to
        represent the given value as an instance of this class."""
        class_name = cls.__name__
        return '%s(%s)' % (class_name, repr(value))

    def pythonLiteral (self):
        """Return a string which can be embedded into Python source to
        represent the value of this instance."""
        return self.PythonLiteral(self)

    def toDOM (self, tag=None, document=None, parent=None):
        (document, element) = domutils.ToDOM_startup(document, parent)
        return element.appendChild(document.createTextNode(self.xsdLiteral()))


class STD_union (simpleTypeDefinition):
    """Base class for union datatypes.

    This class descends only from simpleTypeDefinition.  A LogicError is raised
    if an attempt is made to construct an instance of a subclass of
    STD_union.  Values consistent with the member types are
    constructed using the Factory class method.  Values are validated
    using the _ValidateMember class method.

    Subclasses must provide a class variable _MemberTypes which is a
    tuple of legal members of the union."""

    # Ick: If we don't declare this here, this class's map doesn't get
    # initialized.  Alternative is to not descend from simpleTypeDefinition.
    # @todo Ensure that pattern and enumeration are valid constraints
    __FacetMap = {}

    @classmethod
    def Factory (cls, *args, **kw):
        """Given a value, attempt to create an instance of some member
        of this union.

        The first instance which can be legally created is returned.
        If no member type instance can be created from the given
        value, a BadTypeValueError is raised.

        The value generated from the member types is further validated
        against any constraints that apply to the union."""
        rv = None
        validate_constraints = kw.get('validate_constraints', True)
        for mt in cls._MemberTypes:
            try:
                rv = mt(*args, **kw)
                break
            except BadTypeValueError:
                pass
            except ValueError:
                pass
            except:
                pass
        if rv is not None:
            if validate_constraints:
                cls.XsdConstraintsOK(rv)
            return rv
        raise BadTypeValueError('%s cannot construct union member from args %s' % (cls.__name__, args))

    @classmethod
    def _ValidateMember (cls, value):
        """Validate the given value as a potential union member.

        Raises BadTypeValueError if the value is not an instance of a
        member type."""
        if not isinstance(value, cls._MemberTypes):
            raise BadTypeValueError('%s cannot hold a member of type %s' % (cls.__name__, value.__class__.__name__))
        return value

    def __init__ (self, *args, **kw):
        raise LogicError('%s: cannot construct instances of union' % (self.__class__.__name__,))

class STD_list (simpleTypeDefinition, types.ListType):
    """Base class for collection datatypes.

    This class descends from the Python list type, and incorporates
    simpleTypeDefinition.  Subclasses must define a class variable _ItemType
    which is a reference to the class of which members must be
    instances."""

    # Ick: If we don't declare this here, this class's map doesn't get
    # initialized.  Alternative is to not descend from simpleTypeDefinition.
    __FacetMap = {}

    @classmethod
    def _ValidateItem (cls, value):
        """Verify that the given value is permitted as an item of this list."""
        if issubclass(cls._ItemType, STD_union):
            cls._ItemType._ValidateMember(value)
        else:
            if not isinstance(value, cls._ItemType):
                raise BadTypeValueError('Type %s has member of type %s, must be %s' % (cls.__name__, type(value).__name__, cls._ItemType.__name__))
        return value

    @classmethod
    def _XsdConstraintsPreCheck_vb (cls, value):
        """Verify that the items in the list are acceptable members."""
        for v in value:
            cls._ValidateItem(v)
        super_fn = getattr(super(STD_list, cls), '_XsdConstraintsPreCheck_vb', lambda *a,**kw: True)
        return super_fn(value)

    @classmethod
    def _XsdValueLength_vx (cls, value):
        return len(value)

class element (utility._DeconflictSymbols_mixin, object):
    """Base class for any Python class that serves as the binding to
    an XMLSchema element.

    The subclass must define a class variable _TypeDefinition which is
    a reference to the simpleTypeDefinition or complexTypeDefinition
    subclass that serves as the information holder for the element.

    Most actions on instances of these clases are delegated to the
    underlying content object.
    """

    # Reference to the simple or complex type binding that serves as
    # the content of this element.
    # MUST BE SET IN SUBCLASS
    _TypeDefinition = None

    # Reference to the instance of the underlying type
    __realContent = None

    # Reference to the instance of the underlying type, or to that
    # type's content if that is a complex type with simple content.
    __content = None
    
    # Symbols that remain the responsibility of this class.  Any
    # symbols in the type from the content are deconflicted by
    # providing an alternative name in the subclass.  See the
    # _DeconflictSymbols_mixin class.
    _ReservedSymbols = set([ 'content', 'CreateFromDOM', 'toDOM' ])

    # Assign to the content field.  This may manipulate the assigned
    # value if doing so results in a cleaner interface for the user.
    def __setContent (self, content):
        self.__realContent = content
        self.__content = self.__realContent
        if content is not None:
            if issubclass(self._TypeDefinition, CTD_simple):
                self.__content = self.__realContent.content()
        return self

    def __init__ (self, *args, **kw):
        """Create a new element.

        This sets the content to be an instance created by invoking
        the Factory method of the element type definition.
        
        If the element is a complex type with simple content, the
        value of the content() is dereferenced once, as a convenience.
        """
        self.__setContent(self._TypeDefinition.Factory(*args, **kw))
        
    # Delegate unrecognized attribute accesses to the content.
    def __getattr__ (self, name):
        return getattr(self.__content, name)

    def content (self):
        """Return the element content, which is an instance of the
        _TypeDefinition for this class.  Or, in the case that
        _TypeDefinition is a complex type with simple content, the
        dereferenced simple content is returned."""
        if isinstance(self.__content, CTD_mixed):
            return self.__content.content()
        return self.__content
    
    @classmethod
    def CreateFromDOM (cls, node):
        """Create an instance of this element from the given DOM node.

        Raises LogicError if the name of the node is not consistent
        with the _XsdName of this class."""
        node_name = node.nodeName
        if 0 < node_name.find(':'):
            node_name = node_name.split(':')[1]
        if cls._XsdName != node_name:
            raise UnrecognizedContentError('Attempting to create element %s from DOM node named %s' % (cls._XsdName, node_name))
        rv = cls(validate_constraints=False)
        rv.__setContent(cls._TypeDefinition.CreateFromDOM(node))
        if isinstance(rv, simpleTypeDefinition):
            rv.xsdConstraintsOK()
        return rv

    def toDOM (self, document=None, parent=None):
        """Add a DOM representation of this element as a child of
        parent, which should be a DOM Node instance."""
        (document, element) = domutils.ToDOM_startup(document, parent, self._XsdName)
        self.__realContent.toDOM(tag=None, document=document, parent=element)
        return element

class enumeration_mixin (object):
    """Marker in case we need to know that a PST has an enumeration constraint facet."""
    pass

class complexTypeDefinition (utility._DeconflictSymbols_mixin, object):
    """Base for any Python class that serves as the binding for an
    XMLSchema complexType.

    Subclasses should define a class-level _AttributeMap variable
    which maps from the unicode tag of an attribute to the
    AttributeUse instance that defines it.  Similarly, subclasses
    should define an _ElementMap variable.
    """

    # If the type supports wildcard attributes, this describes their
    # constraints.  (If it doesn't, this should remain None.)
    # Supporting classes should override this value.
    _AttributeWildcard = None

    # Map from ncNames in the binding namespace to AttributeUse
    # instances
    _AttributeMap = { }

    # A value that indicates whether the content model for this type
    # supports wildcard elements.  Supporting classes should override
    # this value.
    _HasWildcardElement = False

    # Map from ncNames in the binding namespace to ElementUse
    # instances
    _ElementMap = { }

    # Per-instance map from tags to attribute values for wildcard
    # attributes.  Value is None if the type does not support wildcard
    # attributes.
    __wildcardAttributeMap = None

    def wildcardAttributeMap (self):
        """Obtain access to wildcard attributes.

        The return value is None if this type does not support
        wildcard attributes.  If wildcard attributes are allowed, the
        return value is a map from tags to the unicode string value of
        the corresponding attribute."""
        return self.__wildcardAttributeMap

    # Per-instance list of DOM nodes interpreted as wildcard elements.
    # Value is None if the type does not support wildcard elements.
    __wildcardElements = None

    def wildcardElements (self):
        """Obtain access to wildcard elements.

        The return value is None if the content model for this type
        does not support wildcard elements.  If wildcard elements are
        allowed, the return value is a list of DOM Element nodes
        corresponding to conformant unrecognized elements, in the
        order in which they were encountered."""
        return self.__wildcardElements

    def __init__ (self, *args, **kw):
        if self._AttributeWildcard is not None:
            self.__wildcardAttributeMap = { }
        if self._HasWildcardElement:
            self.__wildcardElements = []
        super(complexTypeDefinition, self).__init__(*args, **kw)
        that = None
        if 0 < len(args):
            if isinstance(args[0], self.__class__):
                that = args[0]
            else:
                raise IncompleteImplementationError('No constructor support for argument %s' % (args[0],))
        if isinstance(self, _CTD_content_mixin):
            self._resetContent()
        for fu in self._PythonMap().values():
            fu.reset(self)
            iv = None
            if that is not None:
                iv = fu.value(that)
            iv = kw.get(fu.pythonField(), iv)
            if iv is not None:
                fu.setValue(self, iv)
           

    @classmethod
    def Factory (cls, *args, **kw):
        """Create an instance from parameters and keywords."""
        rv = cls(*args, **kw)
        return rv

    @classmethod
    def CreateFromDOM (cls, node):
        """Create an instance from a DOM node.

        Note that only the node attributes and content are used; the
        node name must have been validated against an owning
        element."""
        rv = cls()
        rv._setAttributesFromDOM(node)
        rv._setContentFromDOM(node)
        return rv

    # Specify the symbols to be reserved for all CTDs.
    _ReservedSymbols = set([ 'Factory', 'CreateFromDOM', 'toDOM' ])

    # Class variable which maps complex type attribute names to the
    # name used within the generated binding.  For example, if
    # somebody's gone and decided that the word Factory would make an
    # awesome attribute for some complex type, the binding will
    # rewrite it so the accessor method is Factory_.  This is only
    # overridden in generated bindings where an attribute name
    # conflicted with a reserved symbol.
    _AttributeDeconflictMap = { }

    # Class variable which maps complex type element names to the name
    # used within the generated binding.  See _AttributeDeconflictMap.
    _ElementDeconflictMap = { }

    # None, or a reference to a ContentModel instance that defines how
    # to reduce a DOM node list to the body of this element.
    _ContentModel = None

    @classmethod
    def __PythonMapAttribute (cls):
        return '_%s_PythonMap' % (cls.__name__,)

    @classmethod
    def _PythonMap (cls):
        return getattr(cls, cls.__PythonMapAttribute(), { })

    @classmethod
    def _UpdateElementDatatypes (cls, datatype_map):
        for (k, v) in datatype_map.items():
            cls._ElementMap[k]._setDataTypes(v)
        python_map = { }
        for eu in cls._ElementMap.values():
            python_map[eu.pythonField()] = eu
        for au in cls._AttributeMap.values():
            python_map[au.pythonField()] = au
        assert(len(python_map) == (len(cls._ElementMap) + len(cls._AttributeMap)))
        setattr(cls, cls.__PythonMapAttribute(), python_map)

    @classmethod
    def _UseForElement (cls, element):
        for eu in cls._ElementMap.values():
            if element in eu.validElements():
                return eu
        return None

    @classmethod
    def _UseForTag (cls, tag):
        return cls._ElementMap[tag]

    def _setAttributesFromDOM (self, node):
        """Initialize the attributes of this element from those of the DOM node.

        Raises UnrecognizedAttributeError if the DOM node has
        attributes that are not allowed in this type.  May raise other
        errors if prohibited or required attributes are not
        present."""
        
        # Handle all the attributes that are present in the node
        attrs_available = set(self._AttributeMap.values())
        for ai in range(0, node.attributes.length):
            attr = node.attributes.item(ai)
            local_name = attr.localName
            namespace_name = attr.namespaceURI
            # Ignore xmlns attributes; DOM got those
            if pywxsb.Namespace.XMLNamespaces.uri() == namespace_name:
                continue
            prefix = attr.prefix
            if not prefix:
                prefix = None
            value = attr.value
            # @todo handle cross-namespace attributes
            if prefix is not None:
                raise IncompleteImplementationError('No support for namespace-qualified attributes like %s:%s' % (prefix, local_name))
            au = self._AttributeMap.get(local_name, None)
            if au is None:
                if self._AttributeWildcard is None:
                    raise UnrecognizedAttributeError('Attribute %s is not permitted in type' % (local_name,))
                self.__wildcardAttributeMap[local_name] = value
                continue
            au.setFromDOM(self, node)
            attrs_available.remove(au)
        # Handle all the ones that aren't present.  NB: Don't just
        # reset the attribute; we need to check for missing ones.
        for au in attrs_available:
            au.setFromDOM(self, node)
        return self

    def _setContentFromDOM_vx (self, node):
        """Override this in subclasses that expect to process content."""
        raise LogicError('%s did not implement _setContentFromDOM_vx' % (self.__class__.__name__,))

    def _setContentFromDOM (self, node):
        """Initialize the content of this element from the content of the DOM node."""
        return self._setContentFromDOM_vx(node)

    def _setDOMFromAttributes (self, element):
        """Add any appropriate attributes from this instance into the DOM element."""
        for au in self._AttributeMap.values():
            au.addDOMAttribute(self, element)
        return element

    def toDOM (self, document=None, parent=None, tag=None):
        """Create a DOM element with the given tag holding the content of this instance."""
        (document, element) = domutils.ToDOM_startup(document, parent, tag)
        for eu in self._ElementMap.values():
            eu.clearGenerationMarkers(self)
        self._setDOMFromContent(document, element)
        for eu in self._ElementMap.values():
            if eu.hasUngeneratedValues(self):
                raise DOMGenerationError('Values in %s were not converted to DOM' % (eu.pythonField(),))
        self._setDOMFromAttributes(element)
        return element

class CTD_empty (complexTypeDefinition):
    """Base for any Python class that serves as the binding for an
    XMLSchema complexType with empty content."""

    def _setContentFromDOM_vx (self, node):
        """CTD with empty content does nothing with node content."""
        # @todo Schema validation check?
        return self

    def _setDOMFromContent (self, document, element):
        return self

class CTD_simple (complexTypeDefinition):
    """Base for any Python class that serves as the binding for an
    XMLSchema complexType with simple content."""

    __content = None
    def content (self):
        return self.__content

    def __setContent (self, value):
        self.__content = value

    def __init__ (self, *args, **kw):
        assert issubclass(self._TypeDefinition, simpleTypeDefinition)
        super(CTD_simple, self).__init__(**kw)
        self.__setContent(self._TypeDefinition.Factory(*args, **kw))

    @classmethod
    def Factory (cls, *args, **kw):
        rv = cls(*args, **kw)
        return rv

    def _setContentFromDOM_vx (self, node):
        """CTD with simple content type creates a PST instance from the node body."""
        self.__setContent(self._TypeDefinition.CreateFromDOM(node))

    def _setDOMFromContent (self, document, element):
        """Create a DOM element with the given tag holding the content of this instance."""
        return element.appendChild(document.createTextNode(self.content().xsdLiteral()))

class _CTD_content_mixin (object):
    """Retain information about element and mixed content in a complex type instance.

    This is used to generate the XML from the binding in the same
    order as it was read in, with mixed content in the right position.
    It can also be used if order is critical to the interpretation of
    interleaved elements.

    Subclasses must define a class variable _Content with a
    bindings.Particle instance as its value.

    Subclasses should define a class-level _ElementMap variable which
    maps from unicode element tags (not including namespace
    qualifiers) to the corresponding ElementUse information
    """

    # A list containing just the content
    __content = None

    def __init__ (self, *args, **kw):
        self._resetContent()
        super(_CTD_content_mixin, self).__init__(*args, **kw)

    def content (self):
        return ''.join([ _x for _x in self.__content if isinstance(_x, types.StringTypes) ])

    def _resetContent (self):
        self.__content = []

    def _addElement (self, element):
        eu = self._ElementMap.get(element._XsdName, None)
        if eu is None:
            raise LogicError('Element %s is not registered within CTD %s' % (element._XsdName, self.__class__.__name__))
        eu.setValue(self, element)

    def _addContent (self, child):
        assert isinstance(child, element) or isinstance(child, types.StringTypes)
        self.__content.append(child)

    __isMixed = False
    def _stripMixedContent (self, node_list):
        while 0 < len(node_list):
            if not (node_list[0].nodeType in (dom.Node.TEXT_NODE, dom.Node.CDATA_SECTION_NODE)):
                break
            cn = node_list.pop(0)
            if self.__isMixed:
                #print 'Adding mixed content'
                self._addContent(cn.data)
            else:
                #print 'Ignoring mixed content'
                pass
        return node_list

    def _setMixableContentFromDOM (self, node, is_mixed):
        """Set the content of this instance from the content of the given node."""
        #assert isinstance(self._Content, Particle)
        # The child nodes may include text which should be saved as
        # mixed content.  Use _stripMixedContent prior to extracting
        # element data to save them in the correct relative position,
        # while not losing track of where we are in the content model.
        self.__isMixed = is_mixed
        node_list = node.childNodes[:]
        #print 'Setting mixable control of %s from %s' % (self.__class__, node_list)
        self._stripMixedContent(node_list)
        if self._ContentModel is not None:
            self._ContentModel.interprete(self, node_list)
            self._stripMixedContent(node_list)
        if 0 < len(node_list):
            raise ExtraContentError('Extra content starting with %s' % (node_list[0],))
        return self

    def _setDOMFromContent (self, document, element):
        self._Content.extendDOMFromContent(document, element, self)
        mixed_content = self.content()
        if 0 < len(mixed_content):
            element.appendChild(document.createTextNode(''.join(mixed_content)))
        return self

class CTD_mixed (_CTD_content_mixin, complexTypeDefinition):
    """Base for any Python class that serves as the binding for an
    XMLSchema complexType with mixed content.
    """

    def _setContentFromDOM_vx (self, node):
        """Delegate processing to content mixin, with mixed content enabled."""
        return self._setMixableContentFromDOM(node, is_mixed=True)


class CTD_element (_CTD_content_mixin, complexTypeDefinition):
    """Base for any Python class that serves as the binding for an
    XMLSchema complexType with element-only content.
    """

    def _setContentFromDOM_vx (self, node):
        """Delegate processing to content mixin, with mixed content disabled."""
        return self._setMixableContentFromDOM(node, is_mixed=False)
