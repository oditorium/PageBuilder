"""
merge-transform dicts

This module serves to merge-transform dicts, where the dicts _applied_
later add to those applied earlier, and overwrite them for keys that
exist in both.  

(c) Copyright Stefan LOESCH 2018. All rights reserved.
Licensed under the MIT License
<https://opensource.org/licenses/MIT>
"""
__version__ = "1.0"

import json
import yaml


class Transformer():
    """
    successive merging of dicts

    USAGE

        from transformer import Transformer, transform
        
        tf1 = {'a': 1, 'b':1 }
        tf2 = {'a': 2, 'c': 2}
        transform([tf1, tf2])       # {'a':2, 'b':1, 'c':2}

        # alternative
        Transformer()([tf1, tf2])   # same

        
    """
    
    DELETE_NONE_VALUES = True
    
    def _merge_key_into_dict(s, key, value, target):
        """
        merges {key: value} into the target dict (which is modified)

        - if the key does not exist yet, the pair key: value is simply added
        - if the keys does exist, then
            - if 
        """
        try:
            target_value = target[key]

        except KeyError:
            if not value is None or not s.DELETE_NONE_VALUES:
                target[key] = value
            return

        if isinstance(target_value, dict) and isinstance(value, dict):
            target[key] = s.apply(value, target_value)

        else:
            if value is None and s.DELETE_NONE_VALUES:
                del target[key]
            else:
                target[key] = value
    
    def apply(s, transformation, target):
        """
        apply single transformation dict to the target dict
        
        :transformation:    the transformation dict to apply
        :target:            the target dict where the transformation is applied
                            (will be modified!)
        :returns:           the target dict
        """
        for key, value in transformation.items():
            s._merge_key_into_dict(key, value, target)
        return target
    
    @classmethod
    def toYAML(cls, obj):
        """
        converts single dict to YAML, and iterable of dicts to YAML stream
        """
        if isinstance(obj, dict):
            return yaml.dump(obj, default_flow_style=False)
        else:
            return yaml.dump_all(obj, default_flow_style=False)
        
    @classmethod
    def toJSON(cls, obj):
        """
        converts object to JSON
        """
        return json.dumps(obj)
    
    @classmethod
    def load(cls, yaml_or_json):
        """
        expects a yaml or json file and converts it to generator of dicts
        """
        try:
            result = yaml.safe_load_all(yaml_or_json)
        except:
            try:
                result = json.loads(yaml_or_json)
                if isinstance(result, dict): 
                    result = (result for _ in range(1))
            except:
                result = None

        return result
        
    
    def __call__(s, transformations, target=None, asYAML=False):
        """
        apply (iterable of) transformation dict(s) to the target dict
        
        :transformations:       (iterable of) transformation dict(s)
        :target:                target dict (default: {})
        :returns:               the target dict
        """
        if target is None: target = {}
        
        # if a dict => wrap in generator
        if isinstance(transformations, dict):
            transformations = (transformations for _ in range(1))
         
        # if a string or bytes => assume it is YAML or JSON
        elif isinstance(transformations, str):
            transformations = s.load(transformations)
        elif isinstance(transformations, bytes):
            transformations = s.load(transformations.decode())
            
        for transformation in transformations:
                s.apply(transformation, target)
                
        if asYAML: return s.toYAML(target)
        else: return target

transform = Transformer()
