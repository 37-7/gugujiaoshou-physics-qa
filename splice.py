import os
base = r'C:/Users/Jerry/WorkBuddy/2026-08-25-15-05-40'
src_path = os.path.join(base, 'gen_multi_episode.py')
tpl_path = os.path.join(base, 'new_template.html')
with open(src_path, encoding='utf-8') as f:
    src = f.read()
with open(tpl_path, encoding='utf-8') as f:
    tpl = f.read()

marker = 'HTML = r"""'
assert marker in src, 'marker not found'
i = src.index(marker) + len(marker)
j = src.index('\n"""', i)
new_src = src[:i] + '\n' + tpl + '\n"""' + src[j + len('\n"""'):]

old_tail = "with open(OUT, 'w', encoding='utf-8') as f:\n    f.write(HTML)\nprint('OK 输出:', os.path.basename(OUT))"
new_tail = ("with open(OUT, 'w', encoding='utf-8') as f:\n    f.write(HTML)\n"
            "with open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8') as f:\n    f.write(HTML)\n"
            "print('OK 输出:', os.path.basename(OUT), '| index.html')")
if old_tail in new_src:
    new_src = new_src.replace(old_tail, new_tail)
else:
    assert new_tail in new_src, 'tail already patched but missing?'

with open(src_path, 'w', encoding='utf-8') as f:
    f.write(new_src)
print('spliced OK, new length =', len(new_src))
