# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


# note: most types of words (extension, memory key, ...)
#       are deprecated, and possibly not working. This needs cleanup.
#       Just turns out that in practice, only "component" (i.e. python function)
#       is really useful.

class Word:
    
    types = [ "fractal",
              "component",
              "property",
              "extension",
              "token",
              "grammar",
              "memory_key",
              "scheme" ]

    __slots__ = ["name","type","origin","line",
                 "code","class_","kwargs","related_properties"]
    
    def __init__( self,
                  name,
                  type_,
                  origin,
                  line,
                  code,
                  class_,
                  kwargs={},
                  related_properties=[] ):
        
        if type_ not in self.types :
            raise Exception("cound not create a word of type : "+
                            str(type_)+", authorized types : "+" ".join(self.types))

        self.name = name
        self.type = type_
        self.origin = origin
        self.line = line
        self.code = code
        self.class_ = class_
        self.kwargs = kwargs
        self.related_properties = related_properties

        
    def __repr__(self):
        return repr( {k:repr(getattr(self,k))
                      for k in ['name',
                                'type',
                                'origin',
                                'code',
                                'class_']} )

    
    def __str__(self):
        return str(self.type)+" : "+str(self.name)

    
    def origin_message(self):
        s = self.type+" "+self.name
        if self.origin :
            s+=" ("+self.origin
            if self.line: s+=" line "+str(self.line)
            s+=")"
        return s

    
    def raise_(self,message):
        s = self.origin_message()
        s+=" : "
        raise Exception(s+message)

    
    def __gt__(self,other_word):
        return len(self.name)>len(other_word.name)

    
    @staticmethod
    def check_type(*types):
        for type_ in types:
            if type_ not in _word.types :
                raise Exception(str(type_)+" : unknown type (known types : "
                                +" ".join(_word.types)+")")

