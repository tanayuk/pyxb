from raw.soap import *
import pyxb.standard.bindings.raw.soap as raw_soap
from pyxb.standard.bindings.wsdl import _WSDL_binding_mixin, _WSDL_tBinding_mixin

class tBinding (raw_soap.tBinding, _WSDL_tBinding_mixin):
    pass
raw_soap.tBinding._SetClassRef(tBinding)

class binding (raw_soap.binding, _WSDL_binding_mixin):
    pass
raw_soap.binding._SetClassRef(binding)