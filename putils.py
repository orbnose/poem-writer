import sys
from poem.config import configureDjango

def print_usage():
    print("Usage: ")
    print("\textract [dir]: extract words from books into the db")

if __name__ == "__main__":
    
    #Configure Django
    configureDjango()

    #Django references must be import after Django is configured
    from poem.extract import extract_books
    from poem.make_sentence import make_line

    # Process Args
    try:
        arg = sys.argv[1]

        # --- extract ---
        if arg == 'extract':
            book_dir = sys.argv[2]
            if not book_dir:
                print("Please specify the book directory (e.g. books/")
            else:
                extract_books(book_dir)

        # --- make poem line ---
        elif arg == 'makeline':
            make_line()
        
        # ---- print usage ---
        else:
            print_usage()

    except IndexError:
        print_usage()
