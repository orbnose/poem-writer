from .create import Line, makeline

def make_line():

    # control panel
    num_words = 16
    singular = True
    voice = 'third'
    verb_tense = 'indicative present'

    # make line
    line = makeline(num_words, singular, voice, verb_tense)
    print('\n')
    print( line.get_line_text() )
    print('\n')
    for x, dep_ in enumerate(line.dependency_labels):
        print( dep_, '-', line.pos_tags[x], ' ')