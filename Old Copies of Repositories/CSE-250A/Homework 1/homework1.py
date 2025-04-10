import numpy as np

# Read the words and counts from the file
file = open("hw1_word_counts_05.txt","r")

# Loop through all the elements in the file to get its contents
data = []  # List of tuples where the tuple is in the form of (word, count)
for item in file:
    # Split the word and count
    word, count = item.split()
    
    # Only consider words of length 5 for the Hangman game
    if(len(word) == 5):
        # Create a tuple in the form of (word, count) if we're considering this word
        data.append((word, int(count)))


# Problem A: As a sanity check, print out the fifteen most frequent 5-letter words,
#            as well as the fourteen least frequent 5-letter words. Do your results
#            make sense?

# Sort the list of tuples
# data.sort(key = lambda x: x[1])

# Answer the question
print("Most frequent 15 words: " + str(data[len(data) - 15:]))
print("\nLeast frequent 14 words: " + str(data[:14]))
print()


# Problem B: Indicate the best next guess — namely, the letter ℓ that is most likely
#            (probable) to be among the missing letters. Also report the probability
#            P(Li = ℓ for some i ∈ {1, 2, 3, 4, 5}|E) for your guess ℓ.

# For the purpose of indexing, convert the ascii characters to values indexed by 0
indexed_words = []  # List containing each word in the form of a character list of size 5
for item in data:
    word = item[0]  # Get the word

    # Create a list of chars based on the word. Also, convert them to ints indexed by 0
    char_index_array = [(ord(char) - ord('A')) for char in word] 
    
    indexed_words.append(char_index_array)

# Let's create an array containing the correct evidence (correctly-guessed letters in
# the current Hangman game) for each problem in part B.
# Note: All -1's indicate that there's no correct guess at this position yet
list_correct_evidence = [[-1, -1, -1, -1, -1],
                         [-1, -1, -1, -1, -1],
                         [0, -1, -1, -1, 18],
                         [0, -1, -1, -1, 18],
                         [-1, -1, 14, -1, -1],
		                 [-1, -1, -1, -1, -1],
                         [3, -1, -1, 8, -1],
                         [3, -1, -1, 8, -1],
                         [-1, 20, -1, -1, -1]]

# Do the same for the incorrect evidence (set of indexed characters that were incorrect
# guesses).
list_incorrect_evidence = [[],
                           [0, 4],
                           [],
                           [8],
                           [0, 4, 12, 13, 19],
                           [4, 14],
                           [],
                           [0],
                           [0, 4, 8, 14, 18]]

# For the rest of the homework, it's better if we split the list of tuples into two lists
_, counts = zip(*data)
# We already have words (indexed_words)
counts = np.array(list(counts))

# Before we solve each problem, we need to compute P(W = w) for each word in our data
total_word_count = sum(counts)
words_probability = counts / float(total_word_count)

### Some helper functions

# Determine if we should prune this word because an incorrectly-guessed letter appears in it
def check_incorrect(indexed_word, incorrect_guess_list):
    # All we have to do is check if the two lists have any common elements.
    # If this if true, then that means the word does contain a letter that
    # was incorrectly guessed, so we should prune it.
    indexed_word_set = set(indexed_word)
    incorrect_guess_set = set(incorrect_guess_list)
    if (indexed_word_set & incorrect_guess_set):
        return True
    return False


# Determine if we should prune this word because the characters in the correct evidence list
# don't match the elements in the same slots in the 5-letter word.
def check_unmatching_evidence(indexed_word, correct_evidence):
    # Loop through all characters in this evidence
    for char_index in range(len(correct_evidence)):
        # Before doing anything, check if this element is -1, which means there's no guess
        char_evidence = correct_evidence[char_index]
        char_word = indexed_word[char_index]
        if(char_evidence == -1):
            # Case 1: There's no guess here. However, check the character at this index
            #         in the word. If that character is one of the correctly-guessed
            #         characters in the element list, then this word isn't viable.
            #         Specifically, it appeared somewhere else in the word.
            if(char_word in correct_evidence):
                return True
        else:
            # Case 2: There is a correct guess in this slot. Check the characters in both
            #         the evidence slot and the word slot. If they don't match, then this
            #         isn't a word we can guess.
            if(char_evidence != char_word):
                return True

    # If we made it this far, then this is a viable word to guess
    return False


# Returns a list of binary values that determines if the word is a viable guess or not
def viable_guess(indexed_words, correct_evidence, incorrect_evidence):
    # A list of size equal to the number of words in our data. Each slot represents
    # whether or not this word is a viable word for our Hangman game based on the
    # evidence we currently have (correct and incorrect)
    processed_words = np.zeros(len(indexed_words))  # Set everything to 0 initiailly
                                                    # Will set 1 if the word is viable.

    # Let's process each word one-by-one
    for index in range(len(indexed_words)):
        # Get the current word
        indexed_word = indexed_words[index]

        # Skip all words that have an incorrectly-guessed letter in it
        if(check_incorrect(indexed_word, incorrect_evidence)):
            continue

        # Skip all words where the characters in the slots of correctly-guessed elements
        # don't match the ones in the word.
        if(check_unmatching_evidence(indexed_word, correct_evidence)):
            continue
            
        # If we passed all these checks, then that means this word is a viable guess
        processed_words[index] = 1
    
    return processed_words


# Now, let's solve each problem one-by-one
NUM_PROBLEMS = len(list_correct_evidence)
indexed_words = np.array(indexed_words)
for problem_number in range(NUM_PROBLEMS):
    # Get our evidence for this problem
    correct_evidence = list_correct_evidence[problem_number]
    incorrect_evidence = list_incorrect_evidence[problem_number]

    # Work on the first part of our probability calculation: P(W = w|E)
    #   - P(E|W = w)                            Numerator
    #   - P(W = w)                              Numerator (already computed)
    #   - Summation(P(E|W = w′) * P(W = w′))    Denominator
    
    # Let's first compute P(E|W = w). The probability is binary, which indicates if the
    # given word in our data list is a viable guess based on our evidence.
    probability_evidence_given_word = viable_guess(indexed_words, correct_evidence, incorrect_evidence)

    # Now, we should compute Summation for each word(P(E|W = w′) * P(W = w′)). This is
    # the total probability of selecting any word that's viable wiht the given evidence.
    probability_all_viable_words = np.sum(words_probability * probability_evidence_given_word)

    # Compute the posterior probability, obtained from Bayes rule, in the problem specification
    posterior_probability = probability_evidence_given_word * words_probability / probability_all_viable_words
    

    # We can compute the next Bayes rule directly:
    # Summation of all words(Sol * p1 - P(L_i = l for some i in set {1, 2, 3, 4, 5}|W = w) * P(W = w|E))
    # Specifically, check every blank in the correct evidence. Match it with the character of the same index
    # in the current word. Add the probability of our posterior probability to that letter. Do this
    # for all words to obtain the summation of the predictive probability for all characters.

    # Create a list to store the predictive probabilities for each character
    predictive_probabilities = np.zeros(26)

    # Loop through all the indexed words
    for index in range(len(indexed_words)):
        # Get the current word
        current_word = indexed_words[index]

        # Find the possible characters to guess based on our current word
        char_set = []   # Keeps track of letters we've already checked. Don't double-count them.
        for char_index in range(len(correct_evidence)):
            evidence_char = correct_evidence[char_index]
            word_char = current_word[char_index]

            # If there's no guess in the evidence yet, let's process this character
            if(evidence_char == -1):
                # Make sure we don't double-count if one letter appears in multiple blanks
                if(word_char in char_set):
                    continue

                # Add the posterior probability to the total predictive probability for this character
                predictive_probabilities[word_char] += posterior_probability[index]
                
                # Add this letter to the set
                char_set.append(word_char)

    # Find the best guess
    best_index = np.where(predictive_probabilities == np.max(predictive_probabilities))[0][0]
    print("Best guess for this problem: " + str(chr((best_index + int(ord('A'))))) + ". Predictive probability: " + str(predictive_probabilities[best_index]))

# OFFSET = 6000
# print(posterior_probability[OFFSET:(OFFSET+50)])
# print(predictive_probabilities)
# print(indexed_words)