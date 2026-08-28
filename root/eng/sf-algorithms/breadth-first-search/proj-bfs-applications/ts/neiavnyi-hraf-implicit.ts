function ladderLengthTS(beginWord: string, endWord: string, wordList: string[]): number {
    const dictSet = new Set(wordList);
    if (!dictSet.has(endWord)) return 0;

    const queue: [string, number][] = [[beginWord, 1]];
    let head = 0;

    while (head < queue.length) {
        const [word, length] = queue[head++];
        if (word === endWord) return length;

        for (let i = 0; i < word.length; i++) {
            for (let c = 97; c <= 122; c++) {
                const char = String.fromCharCode(c);
                const nextWord = word.slice(0, i) + char + word.slice(i + 1);
                if (dictSet.has(nextWord)) {
                    dictSet.delete(nextWord);
                    queue.push([nextWord, length + 1]);
                }
            }
        }
    }
    return 0;
}
