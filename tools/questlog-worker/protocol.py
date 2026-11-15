"""Closed-schema validation for the PINNED Server A OpenAPI (no dependencies)."""
import hashlib
import json
from pathlib import Path
import re
from uuid import UUID

PIN='09f0a4b1160845e321caadc4937726809c38f104b515bc98c8d3f2d50e62d40b'


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
class Invalid(ValueError):pass


def decode(raw):
    if len(raw)>65536:raise Invalid('reply_budget')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise Invalid('duplicate_json_field')
            result[k]=v
        return result
    def constant(value):raise Invalid('non_json_constant')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=constant)


class Contract:
    def __init__(self,path=None):
        raw=Path(path or Path(__file__).with_name('dispatcher.openapi.json')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=PIN:raise Invalid('contract_pin_mismatch')
        self.document=decode(raw)
    def validate(self,name,value):
        self.check(self.document['components']['schemas'][name],value)
        return value
    def check(self,s,v,depth=0):
        if depth>24:raise Invalid('schema_depth')
        if '$ref' in s:
            target=self.document
            for segment in s['$ref'][2:].split('/'):target=target[segment]
            return self.check(target,v,depth+1)
        if 'const' in s and (type(v)!=type(s['const']) or v!=s['const']):raise Invalid('const')
        if 'enum' in s and v not in s['enum']:raise Invalid('enum')
        types=s.get('type');types=[types] if isinstance(types,str) else types
        if types:
            match={'object':type(v) is dict,'array':type(v) is list,'string':type(v) is str,
                   'integer':type(v) is int,'number':type(v) in (int,float),'boolean':type(v) is bool,'null':v is None}
            if not any(match[t] for t in types):raise Invalid('type')
        if isinstance(v,dict):
            if not set(s.get('required',[]))<=set(v):raise Invalid('required')
            properties=s.get('properties',{});extra=set(v)-set(properties)
            additional=s.get('additionalProperties',True)
            if additional is False and extra:raise Invalid('unknown_fields')
            for k,child in v.items():
                if k in properties:self.check(properties[k],child,depth+1)
                elif isinstance(additional,dict):self.check(additional,child,depth+1)
            if len(v)<s.get('minProperties',0) or len(v)>s.get('maxProperties',1000000):raise Invalid('properties_budget')
        if isinstance(v,list):
            if len(v)<s.get('minItems',0) or len(v)>s.get('maxItems',1000000):raise Invalid('items_budget')
            if s.get('uniqueItems') and len({canonical(item) for item in v})!=len(v):raise Invalid('duplicate_items')
            for item in v:
                if 'items' in s:self.check(s['items'],item,depth+1)
        if isinstance(v,str):
            if len(v)<s.get('minLength',0) or len(v)>s.get('maxLength',1000000):raise Invalid('text_budget')
            if 'pattern' in s and re.search(s['pattern'],v) is None:raise Invalid('pattern')
            if s.get('format')=='uuid':
                try:valid=str(UUID(v))==v
                except ValueError:valid=False
                if not valid:raise Invalid('uuid')
        if type(v) in (int,float):
            if v<s.get('minimum',float('-inf')) or v>s.get('maximum',float('inf')):raise Invalid('number_budget')
        for child in s.get('allOf',[]):self.check(child,v,depth+1)
        for keyword in ('oneOf','anyOf'):
            if keyword in s:
                successes=0
                for child in s[keyword]:
                    try:self.check(child,v,depth+1);successes+=1
                    except Invalid:pass
                if successes<1 or (keyword=='oneOf' and successes!=1):raise Invalid(keyword)
        if 'if' in s:
            try:self.check(s['if'],v,depth+1);branch='then'
            except Invalid:branch='else'
            if branch in s:self.check(s[branch],v,depth+1)

