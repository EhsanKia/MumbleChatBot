from collections import defaultdict
import random

markov  = [0]+[defaultdict(list)]*2
markovr = [0]+[defaultdict(list)]*2
STOP_WORD = "\n"


def computeResponse(msg):
    msg = msg.replace("<br />", " ")
    if msg[:6] == ".chat ":
        sentence = generate_sentence(msg[6:], 2)
        if sentence:
            return sentence


def add_to_brain(msg, cl):
    wordlist = msg.split()

    buf = [STOP_WORD] * cl
    for word in wordlist:
        markov[cl][tuple(buf)].append(word)
        del buf[0]
        buf.append(word)
    markov[cl][tuple(buf)].append(STOP_WORD)

    wordlist.reverse()
    buf = [STOP_WORD] * cl
    for word in wordlist:
        markovr[cl][tuple(buf[::-1])].append(word)
        del buf[0]
        buf.append(word)
    markovr[cl][tuple(buf[::-1])].append(STOP_WORD)


def generate_sentence(msg, cl):
    if cl == 0:
        return None

    max_words = 10000
    wordlist = msg.split()

    if len(wordlist) == 0:
        for i in range(10):
            wordlist.append( random.choice(markov[2].keys()) )

    elif len(wordlist) == 1:
        word = wordlist[0]
        after = markov[1][(word,)]
        before = markovr[1][(word,)]
        wordlist = []
        for a in after:
            wordlist.append([word,a])
        for b in before:
            wordlist.append([b,word])

    else:
        words = wordlist[:]
        wordlist = []
        for i in range(len(words) - cl):
            wordlist.append(words[i:i + cl])

    sentences = []
    for piece in wordlist:
        message = piece[:]
        buf = piece
        for i in xrange(max_words):
            try:
                next_word = random.choice(markov[cl][tuple(buf)])
            except IndexError:
                continue
            if next_word == STOP_WORD:
                break

            message.append(next_word)
            del buf[0]
            buf.append(next_word)

        buf = piece
        for i in xrange(max_words):
            try:
                prev_word = random.choice(markovr[cl][tuple(buf)])
            except IndexError:
                continue
            if prev_word == STOP_WORD:
                break
            message = [prev_word] + message
            del buf[-1]
            buf = [prev_word] + buf

        if message:
            sentences.append(' '.join(message))

    best_sentences = []
    for s in sentences:
        if s[0].isupper():
            best_sentences.append(s)

    if best_sentences:
        return random.choice(best_sentences)
    elif sentences:
        return random.choice(sentences)
    else:
        return generate_sentence(msg, cl-1)


def load_brain():
    f = open('training_text.txt', 'r')
    for line in f:
        line = line.strip('\n')
        add_to_brain(line, 2)
        add_to_brain(line, 1)
    print 'Brain Reloaded'
    f.close()

load_brain()

generate_sentence("more testing", 2)