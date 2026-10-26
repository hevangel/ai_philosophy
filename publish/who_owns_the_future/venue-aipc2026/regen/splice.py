# splice.py - substitute the selected candidate blocks into the holes file and
# write the new polished-en.md. Run from publish/who_owns_the_future/.
import io, re

def parse_candidates(path):
    text = io.open(path, encoding='utf-8').read()
    blocks = {}
    for part in text.split('## HOLE ')[1:]:
        label = part.split('\n', 1)[0].strip()
        body = part.split('\n', 1)[1].strip('\n')
        blocks[label] = body.strip()
    return blocks

c1 = parse_candidates('venue-aipc2026/regen/candidate-1.md')
c2 = parse_candidates('venue-aipc2026/regen/candidate-2.md')
c3 = parse_candidates('venue-aipc2026/regen/candidate-3.md')

picks = {
    '1': c1['1'],
    '2': c3['2'],
    '3': c1['3'],
    '4': c3['4'],
    '5': c3['5'],
    '6a': c3['6a'],
    '6b': c3['6b'],
    '7': c3['7'],
    '8': c3['8'],
    '9': c2['9'],
    '10': c1['10'],
}

src = io.open('venue-aipc2026/regen/essay-with-holes.md', encoding='utf-8').read()

def sub(m):
    label = m.group(1)
    return picks[label]

new, n = re.subn(r'\[REGEN HOLE ([0-9ab]+) [^\]]*BUDGET: [^\]]*\]', sub, src)
assert n == 11, 'expected 11 markers, replaced %d' % n
assert '[REGEN HOLE' not in new

io.open('polished-en.md', 'w', encoding='utf-8', newline='\n').write(new)
body = new.split('## References')[0]
print('spliced; markers replaced:', n)
print('total words:', len(new.split()))
print('body words (ex-refs):', len(body.split()))
