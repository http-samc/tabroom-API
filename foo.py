from shared.indexed_list import IndexedList


l = IndexedList[str](lambda s: s, ['foo', 'bar', 'baz'])

print(l, len(l))

del l['foo']

print(l, len(l))

l.delete_entries([
    'bar',
    'baz'
])

print(l, len(l))

l.add_entry('foo')

try:
    l.add_entry('foo')
except Exception as e:
    print(e)

l.upsert_entries(['foo', 'bar'])

l.upsert_entry('foo')

print(l)

for s in l:
    print(s)

l.delete_entries(['foo', 'bar'])

print(l)