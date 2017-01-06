# 目录

- [sqlite](#sqlite)


## DB

- `__init__(self, db_module, keywords)`
- query(sql_query, vars=None, processed=False, _test=False) 返回的是一个storage的迭代器,query里面的storage里面还调用一次dict应该没必要，storage继承了dict,dict可以接受二元组列表,zip函数可以方便的生成二元组迭代器
```
        Execute SQL query `sql_query` using dictionary `vars` to interpolate it.
        If `processed=True`, `vars` is a `reparam`-style list to use 
        instead of interpolating.
        
            >>> db = DB(None, {})
            >>> db.query("SELECT * FROM foo", _test=True)
            <sql: 'SELECT * FROM foo'>
            >>> db.query("SELECT * FROM foo WHERE x = $x", vars=dict(x='f'), _test=True)
            <sql: "SELECT * FROM foo WHERE x = 'f'">
            >>> db.query("SELECT * FROM foo WHERE x = " + sqlquote('f'), _test=True)
            <sql: "SELECT * FROM foo WHERE x = 'f'">
```

- select(tables, vars=None, what='*', where=None, order=None, group=None, limit=None, offset=None, _test=False)
```
        Selects `what` from `tables` with clauses `where`, `order`, 
        `group`, `limit`, and `offset`. Uses vars to interpolate. 
        Otherwise, each clause can be a SQLQuery.
        
            >>> db = DB(None, {})
            >>> db.select('foo', _test=True)
            <sql: 'SELECT * FROM foo'>
            >>> db.select(['foo', 'bar'], where="foo.bar_id = bar.id", limit=5, _test=True)
            <sql: 'SELECT * FROM foo, bar WHERE foo.bar_id = bar.id LIMIT 5'>
            >>> db.select('foo', where={'id': 5}, _test=True)
            <sql: 'SELECT * FROM foo WHERE id = 5'>
```

## sqlite

- SqliteDB(DB)继承DB
- `__init__(**kw)` 可以不用参数
- query(*a, **kw) 查看DB.query