# Author: Faycal Kilali
# Version: 1.1
# Program: Goal-based, Information Theoric, Model-based AI Agent for solving word puzzles.
# Attribution: Dr. Cormier for make_word_list, check_letters, get_wrong_letters, is_consistent methods.

import math

# Function: make_word_list
# Parameters:
#   word_list_fname:   File name (including path) for the word list
#   n_letters:         Number of letters in the word
#   allow_proper_noun: Boolean; allow proper nouns in the word list (default F)
# Returns:
#   wordlist: A list of words meeting the specified criteria
# Purpose:
#   Generates a word list from a dictionary file. The file should be a newline
#   separated list of words. Proper nouns, if any, should include one or more
#   upper-case letters; common nouns should be entirely in lower case.

def make_word_list(wordlist_fname, n_letters, allow_proper_noun=True):
    # Initialization
    wordlist = [] # Initialize to an empty list
    # Open the file containing the list of words
    wordlist_file = open(wordlist_fname, "r")
    # Loop through the lines (words) in the list
    word = wordlist_file.readline()
    while(len(word) > 0):
        # Remove leading and trailing whitespace, if any
        word = word.strip()
        if((len(word) == n_letters) and word.isalpha()):
            if(allow_proper_noun or word.islower()):
                wordlist.append(word)
        # Read next word
        word = wordlist_file.readline()
    # Return the complete word list
    return wordlist

# Function: check_letters
# Parameters:
#   solution: Solution to the puzzle (lower-case)
#   guess:    Current guess for the solution (lower-case)
# Returns:
#   Guess string modified to indicate correct and incorrect letters
# Purpose:
#   Checks each in a guess to see if it is in the right place, in the solution
#   but not in the right place, or not in the solution, and generates a string
#   modifed to indicate the result as follows:
#     --Correct letters are in upper-case
#     --Letters in the wrong position are in lower-case
#     --Letters that do not appear in the solution are replaced with "_"
def check_letters(solution, guess):
    result = ""
    for i in range(len(solution)):
        if guess[i] == solution[i]:
            result = result + guess[i].upper()
        elif guess[i] in solution:
            result = result + guess[i]
        else:
            result = result + "_"
    return result

# Function: get_wrong_letters
# Parameters:
#   guess
#   clue
# Returns:
#   List of letters that are not in the solution
def get_wrong_letters(guess, clue):
    result = []
    for i in range(len(guess)):
        if clue[i] == "_" and guess[i] not in result:
            result.append(guess[i])
    return result

# Function: is_consistent
# Parameters:
#   word:         Word to check
#   clue:         Clue
#   wrongletters: Letters that have been eliminated (None to ignore)
# Returns
#   Boolean value
# Purpose:
#   Checks whether or not a given word is consistent with a clue
def is_consistent(word, clue, wrongletters):
    test = True
    i = 0
    while test and i < len(word):
        test = test and not (clue[i].isupper() and clue[i].lower() != word[i].lower())
        test = test and not (clue[i].islower() and clue[i] not in word.lower())
        test = test and not (clue[i].islower() and word[i] == clue[i])
        if wrongletters is not None:
            test = test and not (word[i] in wrongletters)
        i = i + 1
    return test





def word_ig_solver(X, solution, n_guesses):
    """
    tries to solve the word game using Information Theory through Information Gain.
    :param X: set of words
    :return: last guess made, number of guesses, sequence of guesses
    """
    S = []
    clues = []
    guesses_used = 0
    ## Optional: Arbitrarily choosing the first guess
    # In here, I should figure out how to choose the best initial guess, this should be the one that provides the most distinctive feedback.
    # For now, we'll just choose arbitrarily, given that we haven't made any guess yet.
    #best_guess = X[rand.randint(0, len(X))]
    #S.append(best_guess)
    #E = initialize_entropy(X)  # Optimization, O(1) calculation, assuming we start with no information, not even used

    # Optimization
#    clue = check_letters(solution, S[-1])  # Check the initial best guess
#    clues.append(clue)


#    if (clue == solution.upper()):
#        return f"You won! The statistics are: Best guess: {S[-1]}, Number of guesses: {len(S)}, Guesses made: {S}"
#    guesses_used = guesses_used + 1

    while (guesses_used < n_guesses):
        Y = []
        print(f"Remaining guesses: {n_guesses - guesses_used}, Current solution space: {len(X)} words.")

        # Find the guess that creates the most information gain subset(s)
        max_entropy = float('-inf') # Consolidate larger primitive, float.
        best_guess = None

        for candidate in X:
            _, entropy = simulate_guess_patterns(candidate, X)
            if entropy > max_entropy:
                max_entropy = entropy
                best_guess = candidate

        if best_guess is None:  # Safety check
            print("Warning: No best guess found! Using first available word.")
            best_guess = X[0]  # Fallback just in case

        S.append(best_guess) # Hopefully, we found a best guess, otherwise we'd have a None -- exception check here may help
        clue = check_letters(solution, S[-1]) # Check the latest best guess to get another clue
        clues.append(clue) # Append the clue
        print(f"Trying guess: {S[-1]}")

        if (clue == solution.upper()):
            return f"You won! The statistics are: Best guess: {S[-1]}, Number of guesses: {len(S)}, Guesses made: {S}"

        for word in X:
            word_wrong_letters = get_wrong_letters(best_guess, clue)  # Use the latest clue
            consistent_this_many_times = 0
            for current_clue in clues:  # NOTE: can't use clue here as variable shadowing causes issues
                if is_consistent(word, current_clue, word_wrong_letters):
                    consistent_this_many_times = consistent_this_many_times + 1
                    if consistent_this_many_times == len(clues):  # Fully consistent
                        Y.append(word)

        X = Y # Replace the pointer to our word list with our new subset of valid words
        guesses_used = guesses_used + 1

    return f"You ran out of guesses! The solution was: {solution}. Total guesses made: {len(S)}. Your guesses were: {S}"


def simulate_guess_patterns(guess, X):
    """
    Simulates how well a guess can distinguish between possible solutions
    by counting the different patterns it would create.

    Args:
        guess: The word we're considering guessing
        X: List of words that could be the solution

    Returns:
        pattern_counts: Dictionary mapping patterns to their frequency, this may be overkill
        E: the entropy of the resulting subset

    Note: This function is primarily used to avoid using 'guesses'. It uses instead, the clues, in order to deduce the information gain of a particular word.
    """
    pattern_counts = {}
    E_initial = calculate_entropy(X)

    # See what subset (pattern) would be created by each word. The patterns that are split into even(ish) splits are the best, or as close to it as possible.
    for word in X:
        pattern = check_letters(word, guess)
        if pattern not in pattern_counts:
            pattern_counts[pattern] = []
        pattern_counts[pattern].append(word)

    # Calculate average entropy after this guess
    weighted_subset_entropy = 0
    for subset in pattern_counts.values():
        prob = len(subset) / len(X) # Optimization again
        subset_entropy = calculate_entropy(subset)
        weighted_subset_entropy += prob * subset_entropy

    # Information gain is the difference between initial and weighted subset entropy
    information_gained = information_gain(E_initial, weighted_subset_entropy)

    return pattern_counts, information_gained


def information_gain(E, E_subset):
    """
    Calculates the information gain
    :param E:
    :param E_subset:
    :return: the information gain IG(I(x)) = Entropy_{set-prior-to-this-I(x)-decision}(I(x)) - Entropy_{matching-subset}(I(x)), where matchincg-subset is the subset of all remaining valid choices after making the decision.
    More generally, the formula is  IG(I(x)) = Entropy_{set-prior-to-decision}[I(X)] - Entropy_{pattern_subsets}[I(x)]  \text{(Gain in Information from picking decision }H(I(x)))
    """
    gain = E - E_subset
    return gain


def calculate_entropy(X):
    """
    Calculates the entire entropy of the input
    :param X:
    :return: returns Entropy of X
    """
    E = 0
    for x in X:
        #p_x = probability_unit(x, X) # General case
        p_x = 1 / len(X) # OPTIMIZATION: Because in this word game, we assume there's only one solution, and no duplicate words in our set X.
        I = information_unit(p_x)
        E = E + I * p_x
    return E

def initialize_entropy(X):
    """
    Input: A data structure X containing the relevant data points
    Output: Initial entropy
    """
    E = math.log2(len(X))
    return E

def information_unit(p_x):
    """
    Acquires I(x), the information unit of an element x in X
    :param p_x:
    :return: I(x), the number of bits of information attributed to element x.
    :note: if one observes element x, then they gain I(x) bits of information.
    """

    I = - math.log2(p_x)
    return I

def probability_unit(x, X):
    """
    Calculates the probability of an outcome x of a random variable X occuring, that is, P(X = x).
    :param x:
    :param X:
    :return: P(X = x), denoted as p_x
    """
    samples = 0
    for x in X:
        samples += 1
    return samples/len(X) # Return the probability p_x

# Configure parameters
# Puzzle parameters
n_letters = 5
n_guesses = 5
# Word list parameters
word_list_fname = "linuxwords.txt"
word_list = make_word_list(word_list_fname, n_letters, allow_proper_noun=False)

