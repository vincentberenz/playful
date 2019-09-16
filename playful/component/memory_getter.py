# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


from ..memory.memory import Memory


class Memory_getter(object):


    def __init__(self, **kwargs):
        self._properties = None
        self._property_instances = None
        self._scheme = None
        self._position = None
        self._time_stamp = None
        self._pointers_to_extensions = {}
        self._scheme_id = None
        self._scheme_type = None

        
    def delete(self):

        Memory.delete(self._scheme_id)

        
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):

        self._scheme_id = scheme_id
        self._scheme_type = scheme_type
        self._scheme = Memory.get(self._scheme_id)

        if self._scheme is not None:

            self._properties = self._scheme.get_properties()  # name:lock,value
            self._property_instances = self._scheme.get_property_instances()  # name:instance
            self._position = self._scheme.get_position_property()
            self._time_stamp = self._scheme.get_time_stamp_property()

            
    def get_scheme_id(self):
        return self._scheme_id

    
    def get_scheme_type(self):
        return self._scheme_type

    
    def get_value(self, property_name):

        if property_name in self._property_instances:
            return self._property_instances[property_name].get_value_copy()
        raise Exception("unknown property: " +
                        property_name + " (" + self.name + ")")

    
    def get(self, property_or_extension, **kwargs):

        if self._properties is None:
            return None

        try:

            if property_or_extension in self._properties:
                return self._properties[property_or_extension]  # value,lock

            if property_or_extension in self._pointers_to_extensions:
                return self._pointer_to_extensions[property_or_extension](
                    **kwargs)

            else:
                self._pointers_to_extension[property_or_extension] = self._scheme.get_pointer_to_extension(
                    property_or_extension)
                return self._pointer_to_extensions[property_or_extension](
                    **kwargs)

        except Exception as e:
            raise Exception(
                "failed to get '" +
                str(property_or_extension) +
                "'. " +
                str(e))

        
    def set(self, property_name, value):

        if self._properties is None:
            return None

        try:
            self._properties[property_name].set_value(value)
        except Exception as e:
            raise Exception(
                "failed to set " +
                str(property_name) +
                " to: " +
                str(value))

        
    def update(self, property_name, **kwargs):

        if self._properties is None:
            return None

        try:
            self._property_instances[property_name].update(**kwargs)
        except Exception as e:
            raise Exception(
                "failed to update " +
                str(property_name) +
                " to: " +
                str(kwargs) +
                "\n" +
                str(e))

        
    def get_position(self):

        if self._position is None:
            return None

        position, lock = self._position.get_value()

        if position:
            with lock:
                return [p for p in position]

        else:
            return None

        
    def get_time_stamp(self):

        if self._time_stamp is None:
            return None

        return self._time_stamp.get_value_copy()
