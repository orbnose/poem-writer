import pronoun
p = pronoun.Pronoun()

print( 'other: ', p.transform('other', voice='first', dependency_label='subj', singular=True, force_selection=False) )

print( 'I: ', p.transform('other', voice='first', dependency_label='subj', singular=True, force_selection=True) )

print( 'We: ', p.transform('other', voice='first', dependency_label='subj', singular=False, force_selection=True))

print( 'other: ', p.transform('other', voice='third', dependency_label='subj', singular=True, force_selection=True) )

print( 'others: ', p.transform('other', voice='third', dependency_label='subj', singular=False, force_selection=True) )

print( 'us: ', p.transform('I', voice='first', dependency_label='obj', singular=False, force_selection=True) )

print( 'our: ', p.transform('I', voice='first', dependency_label='poss', singular=False, force_selection=True) )

print( 'your/thine/thy: ', p.transform('it', voice='second', dependency_label='poss', singular=True, force_selection=True) )

print( 'these: ', p.transform('this', voice='third', dependency_label='obj', singular=False, force_selection=True) )