"""Small command catalog and bounded calculator. No shell evaluation or disk indexing."""
import ast
import math
import operator
import os
from pathlib import Path


def calculate(expression):
    if len(expression)>160:raise ValueError('Perhitungan terlalu panjang')
    tree=ast.parse(expression,mode='eval')
    if len(list(ast.walk(tree)))>48:raise ValueError('Perhitungan terlalu rumit')
    operations={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Mod:operator.mod,ast.FloorDiv:operator.floordiv,ast.Pow:operator.pow}
    def value(node):
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):result=node.value
        elif isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):result=(1 if isinstance(node.op,ast.UAdd) else -1)*value(node.operand)
        elif isinstance(node,ast.BinOp) and type(node.op) in operations:
            left,right=value(node.left),value(node.right)
            if isinstance(node.op,ast.Pow) and (abs(right)>12 or abs(left)>1e12):raise ValueError('Pangkat terlalu besar')
            result=operations[type(node.op)](left,right)
        else:raise ValueError('Gunakan angka dan operator aritmetika')
        if type(result) not in (int,float) or not math.isfinite(result) or abs(result)>1e15:raise ValueError('Hasil di luar batas')
        return result
    result=value(tree.body)
    return str(round(result,10)) if isinstance(result,float) else str(result)


def app_catalog():
    import config
    result=[{'name':name.title(),'target':target,'kind':'app'} for name,target in config.APPS.items() if name!='whatsapp']
    roots=[Path(os.environ.get('APPDATA',''))/'Microsoft/Windows/Start Menu/Programs',Path(os.environ.get('PROGRAMDATA','C:/ProgramData'))/'Microsoft/Windows/Start Menu/Programs']
    seen={item['name'].casefold() for item in result}
    for root in roots:
        if not root.is_dir():continue
        for path in root.rglob('*.lnk'):
            if len(result)>=500:break
            name=path.stem
            if name.casefold() in seen:continue
            seen.add(name.casefold());result.append({'name':name,'target':str(path),'kind':'shortcut'})
    return result


def suggestions(query,catalog):
    query=query.strip();matches=[]
    if query:
        try:matches.append({'name':calculate(query.lstrip('=')),'target':query,'kind':'calculation'})
        except (ValueError,SyntaxError,ZeroDivisionError,OverflowError,TypeError):pass
        path=Path(os.path.expandvars(query.strip('"'))).expanduser()
        try:
            if path.is_absolute() and path.exists():matches.append({'name':path.name or str(path),'target':str(path),'kind':'path'})
        except OSError:pass
        if query.startswith(('https://','http://')):matches.append({'name':query,'target':query,'kind':'url'})
    matches.extend(item for item in catalog if not query or query.casefold() in item['name'].casefold())
    return matches[:12]
